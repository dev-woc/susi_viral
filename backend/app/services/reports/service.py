from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import uuid4

from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.core.config import get_settings
from app.db.bootstrap import ensure_default_user, ensure_default_workspace
from app.db.models.report_delivery import ReportDelivery
from app.db.models.scheduled_report import ReportRun, ScheduledReport
from app.db.runtime import session_factory
from app.schemas.report import (
    ReportClipResult,
    ReportConnectorFailure,
    ReportDeliveryChannel,
    ReportDeliveryRead,
    ReportDeliveryStatus,
    ReportFrequency,
    ReportPlatform,
    ReportRunListResponse,
    ReportRunRead,
    ReportSearchRequest,
    ReportStatus,
    ScheduledReportListResponse,
    ScheduledReportRead,
)
from app.schemas.search import Timeframe
from app.services.reports.base import ReportPlan
from app.services.reports.delivery import DeliveryDispatcher
from app.services.reports.extraction import ReportContentDNAExtractor
from app.services.reports.report_graph import ReportGraph


class ReportService:
    def __init__(
        self,
        *,
        settings=None,
        graph: ReportGraph | None = None,
        session_factory_override: sessionmaker[Session] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.graph = graph or ReportGraph(
            dispatcher=DeliveryDispatcher(),
            extractor=ReportContentDNAExtractor(),
        )
        self.session_factory = session_factory_override or session_factory

    def create_report(self, session: Session, payload: ReportSearchRequest) -> ScheduledReportRead:
        workspace = ensure_default_workspace(session, self.settings)
        user = ensure_default_user(session, self.settings, workspace)
        report = ScheduledReport(
            report_id=uuid4().hex,
            workspace_id=workspace.id,
            user_id=user.id,
            name=payload.name,
            query_text=payload.query_text,
            platforms=[platform.value for platform in payload.platforms],
            timeframe=payload.timeframe.value,
            minimum_virality_score=payload.minimum_virality_score,
            result_limit=payload.result_limit,
            format_filters=list(payload.format_filters),
            cadence=payload.cadence.value,
            delivery_channels=[channel.value for channel in payload.delivery_channels],
            delivery_destination=payload.delivery_destination,
            enabled=payload.enabled,
            notes=payload.notes,
        )
        report.next_run_at = self._next_run_at(report.cadence, datetime.now(tz=UTC))
        session.add(report)
        session.commit()
        session.refresh(report)
        return self._scheduled_report_read(session, report)

    def list_reports(self, session: Session) -> ScheduledReportListResponse:
        rows = (
            session.query(ScheduledReport)
            .options(
                selectinload(ScheduledReport.runs).selectinload(ReportRun.deliveries),
            )
            .order_by(ScheduledReport.created_at.desc())
            .all()
        )
        return ScheduledReportListResponse(
            items=[self._scheduled_report_read(session, row) for row in rows]
        )

    def get_report(self, session: Session, report_id: int) -> ScheduledReportRead | None:
        report = (
            session.query(ScheduledReport)
            .options(
                selectinload(ScheduledReport.runs).selectinload(ReportRun.deliveries),
            )
            .filter(ScheduledReport.id == report_id)
            .one_or_none()
        )
        if report is None:
            return None
        return self._scheduled_report_read(session, report)

    def update_report(
        self,
        session: Session,
        report_id: int,
        payload: ReportSearchRequest,
    ) -> ScheduledReportRead | None:
        report = session.get(ScheduledReport, report_id)
        if report is None:
            return None
        report.name = payload.name
        report.query_text = payload.query_text
        report.platforms = [platform.value for platform in payload.platforms]
        report.timeframe = payload.timeframe.value
        report.minimum_virality_score = payload.minimum_virality_score
        report.result_limit = payload.result_limit
        report.format_filters = list(payload.format_filters)
        report.cadence = payload.cadence.value
        report.delivery_channels = [channel.value for channel in payload.delivery_channels]
        report.delivery_destination = payload.delivery_destination
        report.enabled = payload.enabled
        report.notes = payload.notes
        report.updated_at = datetime.now(tz=UTC)
        report.next_run_at = self._next_run_at(report.cadence, report.updated_at)
        session.commit()
        session.refresh(report)
        return self._scheduled_report_read(session, report)

    def disable_report(self, session: Session, report_id: int) -> ScheduledReportRead | None:
        report = session.get(ScheduledReport, report_id)
        if report is None:
            return None
        report.enabled = False
        report.updated_at = datetime.now(tz=UTC)
        session.commit()
        session.refresh(report)
        return self._scheduled_report_read(session, report)

    async def run_report(
        self, session: Session, report_id: int, *, triggered_by: str = "manual"
    ) -> ReportRunRead | None:
        report = (
            session.query(ScheduledReport)
            .options(
                selectinload(ScheduledReport.runs).selectinload(ReportRun.deliveries),
            )
            .filter(ScheduledReport.id == report_id)
            .one_or_none()
        )
        if report is None:
            return None

        previous_run = report.runs[0] if report.runs else None
        run = ReportRun(
            report_run_id=uuid4().hex,
            scheduled_report_id=report.id,
            status=ReportStatus.running.value,
            triggered_by=triggered_by,
        )
        session.add(run)
        session.flush()

        try:
            execution = await self.graph.run(
                self._report_plan(report),
                report_run_id=run.report_run_id,
                previous_snapshot=previous_run.report_snapshot
                if previous_run is not None
                else None,
            )
            run.status = execution.status.value
            run.total_fetched = execution.total_fetched
            run.total_ranked = execution.total_ranked
            run.partial_failures = [
                failure.model_dump(mode="json") for failure in execution.partial_failures
            ]
            run.pattern_summary = dict(execution.pattern_summary)
            run.pattern_deltas = dict(execution.pattern_deltas)
            run.top_clips_snapshot = [clip.model_dump(mode="json") for clip in execution.extracted_clips]
            run.report_snapshot = dict(execution.report_snapshot)
            run.completed_at = execution.completed_at

            for outcome in execution.deliveries:
                delivery = ReportDelivery(
                    delivery_id=uuid4().hex,
                    report_run_id=run.id,
                    channel=outcome.channel.value,
                    destination=outcome.destination,
                    status=outcome.status.value,
                    retryable=outcome.retryable,
                    message=outcome.message,
                    delivery_payload=dict(outcome.payload),
                    completed_at=execution.completed_at,
                )
                session.add(delivery)
                run.deliveries.append(delivery)

            report.last_run_at = execution.completed_at
            report.next_run_at = self._next_run_at(report.cadence, execution.completed_at)
            report.updated_at = execution.completed_at
            session.commit()
        except Exception as exc:  # pragma: no cover - defensive guard
            run.status = ReportStatus.failed.value
            run.partial_failures = [
                {
                    "platform": ReportPlatform.tiktok.value,
                    "stage": "report-run",
                    "message": str(exc),
                    "retryable": True,
                }
            ]
            run.completed_at = datetime.now(tz=UTC)
            session.commit()

        session.refresh(run)
        for delivery in run.deliveries:
            session.refresh(delivery)
        return self._report_run_read(run)

    def list_runs(self, session: Session, report_id: int) -> ReportRunListResponse:
        rows = (
            session.query(ReportRun)
            .options(selectinload(ReportRun.deliveries))
            .filter(ReportRun.scheduled_report_id == report_id)
            .order_by(ReportRun.created_at.desc())
            .all()
        )
        return ReportRunListResponse(items=[self._report_run_read(row) for row in rows])

    def _report_plan(self, report: ScheduledReport) -> ReportPlan:
        return ReportPlan(
            scheduled_report_id=report.id,
            report_id=report.report_id,
            workspace_id=report.workspace_id,
            user_id=report.user_id,
            name=report.name,
            query_text=report.query_text,
            platforms=[ReportPlatform(platform) for platform in report.platforms],
            timeframe=Timeframe(report.timeframe),
            minimum_virality_score=report.minimum_virality_score,
            result_limit=report.result_limit,
            format_filters=list(report.format_filters),
            cadence=report.cadence,
            delivery_channels=[
                ReportDeliveryChannel(channel) for channel in report.delivery_channels
            ],
            delivery_destination=report.delivery_destination,
            notes=report.notes,
            enabled=report.enabled,
        )

    def _scheduled_report_read(
        self, session: Session, report: ScheduledReport
    ) -> ScheduledReportRead:
        latest_run = report.runs[0] if report.runs else None
        return ScheduledReportRead(
            id=report.id,
            report_id=report.report_id,
            workspace_id=report.workspace_id,
            user_id=report.user_id,
            name=report.name,
            query_text=report.query_text,
            platforms=[ReportPlatform(platform) for platform in report.platforms],
            timeframe=Timeframe(report.timeframe),
            minimum_virality_score=report.minimum_virality_score,
            result_limit=report.result_limit,
            format_filters=list(report.format_filters),
            cadence=ReportFrequency(report.cadence),
            delivery_channels=[
                ReportDeliveryChannel(channel) for channel in report.delivery_channels
            ],
            delivery_destination=report.delivery_destination,
            enabled=report.enabled,
            notes=report.notes,
            created_at=report.created_at,
            updated_at=report.updated_at,
            last_run_at=report.last_run_at,
            next_run_at=report.next_run_at,
            latest_run=self._report_run_read(latest_run) if latest_run is not None else None,
        )

    def _report_run_read(self, run: ReportRun) -> ReportRunRead:
        return ReportRunRead(
            id=run.id,
            report_run_id=run.report_run_id,
            scheduled_report_id=run.scheduled_report_id,
            status=ReportStatus(run.status),
            triggered_by=run.triggered_by,
            total_fetched=run.total_fetched,
            total_ranked=run.total_ranked,
            partial_failures=[
                ReportConnectorFailure.model_validate(item) for item in run.partial_failures
            ],
            pattern_summary=dict(run.pattern_summary or {}),
            pattern_deltas=dict(run.pattern_deltas or {}),
            top_clips=[self._clip_from_snapshot(item) for item in run.top_clips_snapshot],
            deliveries=[self._delivery_read(delivery) for delivery in run.deliveries],
            report_snapshot=dict(run.report_snapshot or {}),
            created_at=run.created_at,
            completed_at=run.completed_at,
        )

    def _delivery_read(self, delivery: ReportDelivery) -> ReportDeliveryRead:
        return ReportDeliveryRead(
            id=delivery.id,
            delivery_id=delivery.delivery_id,
            report_run_id=delivery.report_run_id,
            channel=ReportDeliveryChannel(delivery.channel),
            destination=delivery.destination,
            status=ReportDeliveryStatus(delivery.status),
            retryable=delivery.retryable,
            message=delivery.message,
            created_at=delivery.created_at,
            completed_at=delivery.completed_at,
        )

    def _clip_from_snapshot(self, payload: dict[str, object]) -> ReportClipResult:
        content_dna_payload = (
            dict(payload["content_dna"]) if isinstance(payload.get("content_dna"), dict) else {}
        )
        platform_value = payload.get("platform", ReportPlatform.tiktok.value)
        if hasattr(platform_value, "value"):
            platform_value = platform_value.value
        content_platform_value = content_dna_payload.get("platform", ReportPlatform.tiktok.value)
        if hasattr(content_platform_value, "value"):
            content_platform_value = content_platform_value.value
        return ReportClipResult(
            clip_id=str(payload.get("clip_id", "")),
            platform=ReportPlatform(str(platform_value)),
            source_url=str(payload.get("source_url", "")),
            title=str(payload.get("title", "")),
            author_handle=payload.get("author_handle"),
            thumbnail_url=payload.get("thumbnail_url"),
            posted_at=payload.get("posted_at"),
            virality_score=float(payload.get("virality_score", 0.0)),
            transcript_excerpt=payload.get("transcript_excerpt"),
            content_dna={
                "schema_version": content_dna_payload.get("schema_version", "1.0"),
                "clip_id": content_dna_payload.get("clip_id", ""),
                "source_url": content_dna_payload.get("source_url", ""),
                "platform": str(content_platform_value),
                "virality_score": content_dna_payload.get("virality_score", 0.0),
                "posted_at": content_dna_payload.get("posted_at"),
                "niche": content_dna_payload.get("niche"),
                "hook": content_dna_payload.get("hook"),
                "format": content_dna_payload.get("format"),
                "emotion": content_dna_payload.get("emotion"),
                "structure": content_dna_payload.get("structure"),
                "cta": content_dna_payload.get("cta"),
                "replication_notes": content_dna_payload.get("replication_notes"),
                "pattern_tags": list(content_dna_payload.get("pattern_tags", [])),
                "confidence": float(content_dna_payload.get("confidence", 0.0)),
            },
        )

    def _next_run_at(self, cadence: str, created_at: datetime | None) -> datetime | None:
        anchor = created_at or datetime.now(tz=UTC)
        if cadence == "daily":
            return anchor + timedelta(days=1)
        if cadence == "weekly":
            return anchor + timedelta(days=7)
        return None


@lru_cache(maxsize=1)
def get_report_service() -> ReportService:
    return ReportService()
