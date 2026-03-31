from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.schemas.report import (
    ReportClipResult,
    ReportPlatform,
    ReportStatus,
    ScheduledReportRead,
)
from app.services.connectors.base import ConnectorContext, PlatformConnector
from app.services.connectors.tiktok import TikTokConnector
from app.services.connectors.youtube_shorts import YouTubeShortsConnector
from app.services.reports.base import (
    ReportConnector,
    ReportConnectorContext,
    ReportConnectorFailure,
    ReportConnectorResult,
    ReportDeliveryOutcome,
    ReportNormalizedClip,
    ReportPlan,
    score_clip,
)
from app.services.reports.delivery import DeliveryDispatcher
from app.services.reports.extraction import ReportContentDNAExtractor
from app.services.reports.instagram_reels import InstagramReelsConnector
from app.services.reports.reddit import RedditConnector
from app.services.reports.report_builder import (
    build_pattern_deltas,
    build_pattern_summary,
    build_report_snapshot,
)
from app.services.reports.twitter_x import TwitterXConnector

logger = logging.getLogger(__name__)


class _SearchConnectorAdapter(ReportConnector):
    def __init__(self, connector: PlatformConnector, platform: ReportPlatform) -> None:
        self.connector = connector
        self.platform = platform

    async def fetch(self, context: ReportConnectorContext) -> ReportConnectorResult:
        search_context = ConnectorContext(
            search_id=context.report_run_id,
            query=context.query_text,
            timeframe=context.timeframe,
            result_limit=context.result_limit,
            format_filters=context.format_filters,
        )
        result = await self.connector.fetch(search_context)
        clips = [
            ReportNormalizedClip(
                platform=self.platform,
                platform_clip_id=clip.platform_clip_id,
                source_url=clip.source_url,
                title=clip.title,
                description=clip.description,
                author_name=clip.author_name,
                author_handle=clip.author_handle,
                view_count=clip.view_count,
                like_count=clip.like_count,
                comment_count=clip.comment_count,
                share_count=clip.share_count,
                posted_at=clip.posted_at,
                transcript=clip.transcript,
                frame_samples=list(clip.frame_samples),
                raw_payload=dict(clip.raw_payload),
                format_hint=clip.format_hint,
            )
            for clip in result.clips
        ]
        return ReportConnectorResult(
            platform=self.platform, clips=clips, total_available=len(clips)
        )


@dataclass(slots=True)
class ReportGraphState:
    report: ScheduledReportRead
    report_run_id: str
    partial_failures: list[ReportConnectorFailure]
    ranked_clips: list[tuple[ReportNormalizedClip, float]]
    extracted_clips: list[ReportClipResult]
    deliveries: list[ReportDeliveryOutcome]
    pattern_summary: dict[str, int]
    pattern_deltas: dict[str, int]
    total_fetched: int
    total_ranked: int
    status: ReportStatus
    report_snapshot: dict[str, Any]
    completed_at: datetime | None


class ReportGraph:
    def __init__(
        self,
        *,
        connectors: dict[ReportPlatform, ReportConnector] | None = None,
        extractor: ReportContentDNAExtractor | None = None,
        dispatcher: DeliveryDispatcher | None = None,
    ) -> None:
        self.connectors = connectors or self._default_connectors()
        self.extractor = extractor or ReportContentDNAExtractor()
        self.dispatcher = dispatcher or DeliveryDispatcher()

    async def run(
        self,
        plan: ReportPlan,
        *,
        report_run_id: str,
        previous_snapshot: dict[str, Any] | None = None,
    ) -> ReportGraphState:
        context = ReportConnectorContext(
            scheduled_report_id=plan.scheduled_report_id,
            report_run_id=report_run_id,
            query_text=plan.query_text,
            timeframe=plan.timeframe,
            result_limit=plan.result_limit,
            format_filters=plan.format_filters,
        )
        logger.info(
            "starting report run",
            extra={
                "scheduled_report_id": plan.scheduled_report_id,
                "report_run_id": report_run_id,
                "stage": "start",
            },
        )
        results = await asyncio.gather(
            *[self._fetch_platform(platform, context) for platform in plan.platforms],
            return_exceptions=True,
        )
        partial_failures: list[ReportConnectorFailure] = []
        all_clips: list[ReportNormalizedClip] = []
        total_fetched = 0

        for result in results:
            if isinstance(result, Exception):
                logger.exception(
                    "report connector raised unexpectedly",
                    extra={
                        "scheduled_report_id": plan.scheduled_report_id,
                        "report_run_id": report_run_id,
                    },
                )
                continue
            if result.failure is not None:
                partial_failures.append(result.failure)
                continue
            all_clips.extend(result.clips)
            total_fetched += result.total_available

        ranked_clips = sorted(
            ((clip, score_clip(clip, plan.timeframe)) for clip in all_clips),
            key=lambda item: item[1],
            reverse=True,
        )
        ranked_clips = [item for item in ranked_clips if item[1] >= plan.minimum_virality_score][
            : plan.result_limit
        ]

        extracted_clips: list[ReportClipResult] = []
        for clip, score in ranked_clips:
            content_dna = await self.extractor.extract(
                clip,
                query_text=plan.query_text,
                virality_score=score,
            )
            extracted_clips.append(
                ReportClipResult(
                    clip_id=content_dna.clip_id,
                    platform=content_dna.platform,
                    source_url=content_dna.source_url,
                    title=clip.title,
                    author_handle=clip.author_handle,
                    thumbnail_url=None,
                    posted_at=content_dna.posted_at,
                    virality_score=content_dna.virality_score,
                    transcript_excerpt=clip.transcript[:240] if clip.transcript else None,
                    content_dna=content_dna,
                )
            )

        pattern_summary = build_pattern_summary(extracted_clips)
        previous_summary = (
            (previous_snapshot or {}).get("pattern_summary") if previous_snapshot else None
        )
        pattern_deltas = build_pattern_deltas(pattern_summary, previous_summary)

        status = self._derive_status(plan.platforms, partial_failures, extracted_clips)
        completed_at = datetime.now(tz=UTC)
        snapshot = None  # filled below
        deliveries = []
        report_read = ScheduledReportRead(
            id=plan.scheduled_report_id,
            report_id=plan.report_id,
            workspace_id=plan.workspace_id,
            user_id=plan.user_id,
            name=plan.name,
            query_text=plan.query_text,
            platforms=plan.platforms,
            timeframe=plan.timeframe,
            minimum_virality_score=plan.minimum_virality_score,
            result_limit=plan.result_limit,
            format_filters=plan.format_filters,
            cadence=plan.cadence,
            delivery_channels=plan.delivery_channels,
            delivery_destination=plan.delivery_destination,
            enabled=plan.enabled,
            notes=plan.notes,
            created_at=completed_at,
            updated_at=completed_at,
            last_run_at=completed_at,
            next_run_at=None,
            latest_run=None,
        )
        snapshot = build_report_snapshot(
            report=report_read,
            report_run_id=report_run_id,
            status=status,
            total_fetched=total_fetched,
            total_ranked=len(extracted_clips),
            partial_failures=partial_failures,
            pattern_summary=pattern_summary,
            pattern_deltas=pattern_deltas,
            top_clips=extracted_clips,
            deliveries=deliveries,
            completed_at=completed_at,
        )
        deliveries = self.dispatcher.dispatch(report_read, snapshot)
        snapshot = snapshot.model_copy(
            update={"deliveries": [delivery.model_dump(mode="json") for delivery in deliveries]}
        )

        logger.info(
            "completed report run",
            extra={
                "scheduled_report_id": plan.scheduled_report_id,
                "report_run_id": report_run_id,
                "stage": "complete",
            },
        )
        return ReportGraphState(
            report=report_read,
            report_run_id=report_run_id,
            partial_failures=partial_failures,
            ranked_clips=ranked_clips,
            extracted_clips=extracted_clips,
            deliveries=deliveries,
            pattern_summary=pattern_summary,
            pattern_deltas=pattern_deltas,
            total_fetched=total_fetched,
            total_ranked=len(extracted_clips),
            status=status,
            report_snapshot=snapshot.model_dump(mode="json"),
            completed_at=completed_at,
        )

    async def _fetch_platform(
        self,
        platform: ReportPlatform,
        context: ReportConnectorContext,
    ) -> ReportConnectorResult:
        connector = self.connectors[platform]
        try:
            return await connector.fetch(context)
        except Exception as exc:  # pragma: no cover - defensive guard
            return ReportConnectorResult(
                platform=platform,
                clips=[],
                total_available=0,
                failure=ReportConnectorFailure(
                    platform=platform,
                    stage="fetch",
                    message=str(exc),
                    retryable=True,
                ),
            )

    def _derive_status(
        self,
        platforms: list[ReportPlatform],
        partial_failures: list[ReportConnectorFailure],
        extracted_clips: list[ReportClipResult],
    ) -> ReportStatus:
        if len(partial_failures) >= len(platforms) and platforms:
            return ReportStatus.failed
        if partial_failures:
            return ReportStatus.partial
        if extracted_clips:
            return ReportStatus.complete
        return ReportStatus.complete

    def _default_connectors(self) -> dict[ReportPlatform, ReportConnector]:
        return {
            ReportPlatform.tiktok: _SearchConnectorAdapter(
                TikTokConnector(), ReportPlatform.tiktok
            ),
            ReportPlatform.youtube_shorts: _SearchConnectorAdapter(
                YouTubeShortsConnector(),
                ReportPlatform.youtube_shorts,
            ),
            ReportPlatform.instagram_reels: InstagramReelsConnector(),
            ReportPlatform.twitter_x: TwitterXConnector(),
            ReportPlatform.reddit: RedditConnector(),
        }
