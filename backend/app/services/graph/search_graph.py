from __future__ import annotations

import asyncio
from collections import Counter
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.base import session_scope
from app.db.models.content_dna import ContentDNA
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery
from app.schemas.content_dna import ContentDNARead, PatternTagData, PlatformName
from app.schemas.search import (
    ConnectorFailure,
    RawClipRead,
    RankedSearchResult,
    SearchDetailResponse,
    SearchRequest,
    SearchStatus,
    SearchSummary,
)
from app.services.connectors.base import (
    ConnectorContext,
    ConnectorFailure as ConnectorFailureModel,
    ConnectorResult,
    PlatformConnector,
)
from app.services.connectors.tiktok import TikTokConnector
from app.services.connectors.youtube_shorts import YouTubeShortsConnector
from app.services.extraction.content_dna_extractor import ContentDNAExtractor
from app.services.identity import RequestIdentity
from app.services.ranking.virality import RankedClip, ViralityRanker


class SearchGraph:
    def __init__(self, settings: Settings, session_factory: sessionmaker[Session]) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.connectors: dict[PlatformName, PlatformConnector] = {
            PlatformName.tiktok: TikTokConnector(clip_limit=settings.connector_clip_limit),
            PlatformName.youtube_shorts: YouTubeShortsConnector(clip_limit=settings.connector_clip_limit),
        }
        self.extractor = ContentDNAExtractor(settings)
        self.ranker = ViralityRanker()

    async def run(
        self,
        *,
        search_id: str,
        request: SearchRequest,
        identity: RequestIdentity,
    ) -> SearchDetailResponse:
        connector_context = ConnectorContext(
            search_id=search_id,
            query=request.query,
            timeframe=request.timeframe,
            result_limit=request.result_limit or self.settings.search_result_limit,
            format_filters=request.format_filters,
        )
        connector_results = await asyncio.gather(
            *[
                self._fetch_platform(platform, connector_context)
                for platform in request.platforms
                if platform in self.connectors
            ],
            return_exceptions=False,
        )

        failures: list[ConnectorFailure] = []
        fetched_clips = []
        for result in connector_results:
            if result.failure is not None:
                failures.append(
                    ConnectorFailure(
                        platform=result.failure.platform,
                        stage=result.failure.stage,
                        message=result.failure.message,
                        retryable=result.failure.retryable,
                    )
                )
                continue
            fetched_clips.extend(result.clips)

        ranked = self.ranker.rank(
            fetched_clips,
            timeframe=request.timeframe,
            threshold=request.minimum_virality_score,
            limit=request.result_limit or self.settings.search_result_limit,
        )

        with session_scope(self.session_factory) as session:
            search_query = SearchQuery(
                search_id=search_id,
                workspace_id=identity.workspace_id,
                user_id=identity.user_id,
                query_text=request.query,
                platforms=[platform.value for platform in request.platforms],
                timeframe=request.timeframe.value,
                min_virality_score=request.minimum_virality_score,
                result_limit=request.result_limit or self.settings.search_result_limit,
                status=SearchStatus.pending.value,
            )
            session.add(search_query)
            session.flush()

            results: list[RankedSearchResult] = []
            pattern_counts: Counter[str] = Counter()

            for ranked_clip in ranked:
                raw_clip = RawClip(
                    search_query_id=search_query.id,
                    platform=ranked_clip.clip.platform.value,
                    platform_clip_id=ranked_clip.clip.platform_clip_id,
                    source_url=ranked_clip.clip.source_url,
                    title=ranked_clip.clip.title,
                    description=ranked_clip.clip.description,
                    author_name=ranked_clip.clip.author_name,
                    author_handle=ranked_clip.clip.author_handle,
                    view_count=ranked_clip.clip.view_count,
                    like_count=ranked_clip.clip.like_count,
                    comment_count=ranked_clip.clip.comment_count,
                    share_count=ranked_clip.clip.share_count,
                    posted_at=ranked_clip.clip.posted_at,
                    transcript=ranked_clip.clip.transcript,
                    frame_samples=list(ranked_clip.clip.frame_samples),
                    raw_payload=dict(ranked_clip.clip.raw_payload),
                    normalized_score=ranked_clip.normalized_score,
                    rank=ranked_clip.rank,
                    extracted_at=datetime.now(tz=UTC),
                )
                session.add(raw_clip)
                session.flush()

                extracted = await self.extractor.extract(
                    ranked_clip.clip,
                    ranked_clip.normalized_score,
                )
                content_dna = ContentDNA(
                    raw_clip_id=raw_clip.id,
                    schema_version=extracted.schema_version,
                    clip_id=extracted.clip_id,
                    source_url=extracted.source_url,
                    platform=extracted.platform.value,
                    virality_score=extracted.virality_score,
                    posted_at=extracted.posted_at,
                    niche=extracted.niche,
                    hook=extracted.hook,
                    format=extracted.format,
                    emotion=extracted.emotion,
                    structure=extracted.structure,
                    cta=extracted.cta,
                    replication_notes=extracted.replication_notes,
                    confidence=extracted.confidence,
                    extracted_payload=extracted.model_dump(mode="json"),
                )
                session.add(content_dna)
                session.flush()

                for tag_payload in extracted.pattern_tags:
                    tag = (
                        session.query(PatternTag)
                        .filter(
                            PatternTag.name == tag_payload.name,
                            PatternTag.category == tag_payload.category,
                        )
                        .one_or_none()
                    )
                    if tag is None:
                        tag = PatternTag(name=tag_payload.name, category=tag_payload.category)
                        session.add(tag)
                        session.flush()
                    if tag not in content_dna.pattern_tags:
                        content_dna.pattern_tags.append(tag)

                session.flush()
                session.refresh(raw_clip)
                session.refresh(content_dna)

                if content_dna.hook:
                    pattern_counts[f"hook:{content_dna.hook}"] += 1
                if content_dna.format:
                    pattern_counts[f"format:{content_dna.format}"] += 1
                results.append(self._ranked_result(raw_clip, content_dna))

            search_query.status = (
                SearchStatus.failed.value
                if failures and not results
                else SearchStatus.partial.value
                if failures
                else SearchStatus.completed.value
            )
            search_query.partial_failures = [failure.model_dump(mode="json") for failure in failures]
            search_query.pattern_summary = dict(pattern_counts)
            search_query.completed_at = datetime.now(tz=UTC)
            session.flush()
            session.refresh(search_query)

            return SearchDetailResponse(
                search_id=search_query.search_id,
                status=SearchStatus(search_query.status),
                query=search_query.query_text,
                timeframe=request.timeframe,
                minimum_virality_score=search_query.min_virality_score,
                result_limit=search_query.result_limit,
                platforms=request.platforms,
                created_at=search_query.created_at,
                completed_at=search_query.completed_at,
                results=results,
                platform_failures=failures,
                summary=SearchSummary(
                    total_fetched=len(fetched_clips),
                    total_ranked=len(results),
                    total_saved=0,
                    pattern_counts=dict(pattern_counts),
                ),
            )

    async def _fetch_platform(self, platform: PlatformName, context: ConnectorContext):
        connector = self.connectors[platform]
        try:
            return await connector.fetch(context)
        except Exception as exc:
            return ConnectorResult(
                platform=platform,
                clips=[],
                failure=ConnectorFailureModel(
                    platform=platform,
                    stage="fetch",
                    message=str(exc),
                    retryable=True,
                ),
            )

    def _ranked_result(self, raw_clip: RawClip, content_dna: ContentDNA) -> RankedSearchResult:
        return RankedSearchResult(
            raw_clip=self._raw_clip_read(raw_clip, content_dna),
            content_dna=self._content_dna_read(content_dna),
            rank=raw_clip.rank or 0,
            normalized_score=raw_clip.normalized_score,
        )

    def _raw_clip_read(self, raw_clip: RawClip, content_dna: ContentDNA | None = None) -> RawClipRead:
        return RawClipRead(
            id=raw_clip.id,
            search_query_id=raw_clip.search_query_id,
            platform=PlatformName(raw_clip.platform),
            platform_clip_id=raw_clip.platform_clip_id,
            source_url=raw_clip.source_url,
            title=raw_clip.title,
            description=raw_clip.description,
            author_name=raw_clip.author_name,
            author_handle=raw_clip.author_handle,
            view_count=raw_clip.view_count,
            like_count=raw_clip.like_count,
            comment_count=raw_clip.comment_count,
            share_count=raw_clip.share_count,
            posted_at=raw_clip.posted_at,
            transcript=raw_clip.transcript,
            frame_samples=list(raw_clip.frame_samples or []),
            raw_payload=dict(raw_clip.raw_payload or {}),
            normalized_score=raw_clip.normalized_score,
            rank=raw_clip.rank,
            content_dna=self._content_dna_read(content_dna) if content_dna is not None else None,
        )

    def _content_dna_read(self, content_dna: ContentDNA) -> ContentDNARead:
        return ContentDNARead(
            id=content_dna.id,
            raw_clip_id=content_dna.raw_clip_id,
            schema_version=content_dna.schema_version,
            clip_id=content_dna.clip_id,
            source_url=content_dna.source_url,
            platform=PlatformName(content_dna.platform),
            virality_score=content_dna.virality_score,
            posted_at=content_dna.posted_at,
            niche=content_dna.niche,
            hook=content_dna.hook,
            format=content_dna.format,
            emotion=content_dna.emotion,
            structure=content_dna.structure,
            cta=content_dna.cta,
            replication_notes=content_dna.replication_notes,
            pattern_tags=[
                PatternTagData(name=tag.name, category=tag.category)
                for tag in content_dna.pattern_tags
            ],
            confidence=content_dna.confidence,
            created_at=content_dna.created_at,
        )
