from __future__ import annotations

import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.db.base import Base, create_engine_for_url
from app.db.models.report_delivery import ReportDelivery  # noqa: F401
from app.db.models.scheduled_report import ReportRun, ScheduledReport  # noqa: F401
from app.db.models.user import User  # noqa: F401
from app.db.models.workspace import Workspace  # noqa: F401
from app.schemas.report import (
    ReportDeliveryChannel,
    ReportFrequency,
    ReportPlatform,
    ReportSearchRequest,
    ReportStatus,
)
from app.schemas.search import Timeframe
from app.services.reports.service import ReportService
from sqlalchemy.orm import Session, sessionmaker


@contextmanager
def _build_session(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine_for_url(f"sqlite:///{tmp_path / 'pipeline.db'}")
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_report_pipeline_generates_snapshot_and_deliveries(tmp_path: Path) -> None:
    with _build_session(tmp_path) as session:
        service = ReportService()
        report = service.create_report(
            session,
            ReportSearchRequest(
                name="All platform report",
                query_text="growth systems",
                platforms=[
                    ReportPlatform.tiktok,
                    ReportPlatform.youtube_shorts,
                    ReportPlatform.instagram_reels,
                    ReportPlatform.twitter_x,
                    ReportPlatform.reddit,
                ],
                timeframe=Timeframe.week_1,
                minimum_virality_score=10,
                result_limit=5,
                cadence=ReportFrequency.weekly,
                delivery_channels=[
                    ReportDeliveryChannel.dashboard,
                    ReportDeliveryChannel.email,
                    ReportDeliveryChannel.pdf,
                ],
                delivery_destination="ops@example.com",
            ),
        )

        run = asyncio.run(service.run_report(session, report.id, triggered_by="manual"))

        assert run is not None
        assert run.status in {ReportStatus.complete, ReportStatus.partial}
        assert run.total_ranked > 0
        assert run.pattern_summary
        assert len(run.deliveries) == 3
        assert run.report_snapshot["report_run_id"] == run.report_run_id
        assert run.report_snapshot["top_clips"]


def test_report_pipeline_surfaces_partial_failures_without_failing_all_results(
    tmp_path: Path,
) -> None:
    with _build_session(tmp_path) as session:
        service = ReportService()
        report = service.create_report(
            session,
            ReportSearchRequest(
                name="Partial failure report",
                query_text="fail-twitter creator strategy",
                platforms=[
                    ReportPlatform.tiktok,
                    ReportPlatform.twitter_x,
                    ReportPlatform.reddit,
                ],
                timeframe=Timeframe.week_1,
                minimum_virality_score=10,
                result_limit=5,
                cadence=ReportFrequency.weekly,
                delivery_channels=[ReportDeliveryChannel.dashboard],
                delivery_destination=None,
            ),
        )

        run = asyncio.run(service.run_report(session, report.id, triggered_by="manual"))

        assert run is not None
        assert run.status == ReportStatus.partial
        assert any(failure.platform == ReportPlatform.twitter_x for failure in run.partial_failures)
        assert run.total_ranked > 0
