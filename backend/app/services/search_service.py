from __future__ import annotations

from collections import Counter
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker, selectinload

from app.core.config import Settings
from app.db.base import session_scope
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery
from app.schemas.content_dna import ContentDNARead, PatternTagData, PlatformName
from app.schemas.library import LibraryItemCreate, LibraryItemRead
from app.schemas.search import (
    ConnectorFailure,
    RawClipRead,
    RankedSearchResult,
    SearchDetailResponse,
    SearchRequest,
    SearchStatus,
    SearchSummary,
    Timeframe,
)
from app.services.graph.search_graph import SearchGraph
from app.services.identity import RequestIdentity


class SearchService:
    def __init__(self, settings: Settings, session_factory: sessionmaker[Session]) -> None:
        self.settings = settings
        self.session_factory = session_factory
        self.graph = SearchGraph(settings=settings, session_factory=session_factory)

    async def run_search(self, request: SearchRequest, identity: RequestIdentity) -> SearchDetailResponse:
        search_id = uuid4().hex
        return await self.graph.run(search_id=search_id, request=request, identity=identity)

    def get_search(self, search_id: str) -> SearchDetailResponse | None:
        with self.session_factory() as session:
            query = (
                session.query(SearchQuery)
                .options(
                    selectinload(SearchQuery.raw_clips)
                    .selectinload(RawClip.content_dna)
                    .selectinload(ContentDNA.pattern_tags)
                )
                .filter(SearchQuery.search_id == search_id)
                .one_or_none()
            )
            if query is None:
                return None
            return self._search_response_from_query(query)

    def save_library_item(self, identity: RequestIdentity, item: LibraryItemCreate) -> LibraryItemRead:
        with session_scope(self.session_factory) as session:
            existing = (
                session.query(LibraryItem)
                .options(selectinload(LibraryItem.content_dna).selectinload(ContentDNA.raw_clip))
                .filter(
                    LibraryItem.workspace_id == identity.workspace_id,
                    LibraryItem.content_dna_id == item.content_dna_id,
                )
                .one_or_none()
            )
            if existing is not None:
                if item.note is not None and existing.note != item.note:
                    existing.note = item.note
                return self._library_item_response(existing)

            content_dna = session.get(ContentDNA, item.content_dna_id)
            if content_dna is None:
                raise LookupError(f"content_dna_id {item.content_dna_id} not found")

            library_item = LibraryItem(
                workspace_id=identity.workspace_id,
                content_dna_id=content_dna.id,
                note=item.note,
            )
            session.add(library_item)
            session.flush()
            session.refresh(library_item)
            return self._library_item_response(library_item)

    def list_library_items(
        self,
        identity: RequestIdentity,
        platform: str | None = None,
        hook: str | None = None,
    ) -> list[LibraryItemRead]:
        with self.session_factory() as session:
            rows = (
                session.query(LibraryItem)
                .join(LibraryItem.content_dna)
                .join(ContentDNA.raw_clip)
                .options(selectinload(LibraryItem.content_dna).selectinload(ContentDNA.raw_clip))
                .filter(LibraryItem.workspace_id == identity.workspace_id)
                .order_by(LibraryItem.created_at.desc())
            )
            if platform is not None:
                rows = rows.filter(ContentDNA.platform == platform)
            if hook is not None:
                rows = rows.filter(ContentDNA.hook == hook)
            return [self._library_item_response(row) for row in rows.all()]

    def _search_response_from_query(self, query: SearchQuery) -> SearchDetailResponse:
        ranked_clips = [raw_clip for raw_clip in query.raw_clips if raw_clip.rank is not None]
        results: list[RankedSearchResult] = []
        pattern_counts: Counter[str] = Counter()
        for raw_clip in sorted(
            ranked_clips,
            key=lambda row: (row.rank if row.rank is not None else 999, -row.normalized_score),
        ):
            content_dna = raw_clip.content_dna
            if content_dna is not None:
                if content_dna.hook:
                    pattern_counts[f"hook:{content_dna.hook}"] += 1
                if content_dna.format:
                    pattern_counts[f"format:{content_dna.format}"] += 1
            results.append(self._ranked_result(raw_clip))

        return SearchDetailResponse(
            search_id=query.search_id,
            status=SearchStatus(query.status),
            query=query.query_text,
            timeframe=Timeframe(query.timeframe),
            minimum_virality_score=query.min_virality_score,
            result_limit=query.result_limit,
            platforms=[PlatformName(platform) for platform in query.platforms],
            created_at=query.created_at,
            completed_at=query.completed_at,
            results=results,
            platform_failures=[ConnectorFailure.model_validate(failure) for failure in query.partial_failures],
            summary=SearchSummary(
                total_fetched=len(query.raw_clips),
                total_ranked=len(ranked_clips),
                total_saved=0,
                pattern_counts=dict(pattern_counts),
            ),
        )

    def _ranked_result(self, raw_clip: RawClip) -> RankedSearchResult:
        return RankedSearchResult(
            raw_clip=self._raw_clip_read(raw_clip),
            content_dna=self._content_dna_read(raw_clip.content_dna) if raw_clip.content_dna else None,
            rank=raw_clip.rank or 0,
            normalized_score=raw_clip.normalized_score,
        )

    def _raw_clip_read(self, raw_clip: RawClip) -> RawClipRead:
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
            content_dna=self._content_dna_read(raw_clip.content_dna) if raw_clip.content_dna else None,
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
                PatternTagData(name=tag.name, category=tag.category) for tag in content_dna.pattern_tags
            ],
            confidence=content_dna.confidence,
            created_at=content_dna.created_at,
        )

    def _library_item_response(self, item: LibraryItem) -> LibraryItemRead:
        assert item.content_dna is not None
        assert item.content_dna.raw_clip is not None
        return LibraryItemRead(
            id=item.id,
            workspace_id=item.workspace_id,
            content_dna_id=item.content_dna_id,
            note=item.note,
            created_at=item.created_at,
            content_dna=self._content_dna_read(item.content_dna),
            raw_clip=self._raw_clip_read(item.content_dna.raw_clip),
        )

