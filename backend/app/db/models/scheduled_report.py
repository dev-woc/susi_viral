from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.report_delivery import ReportDelivery


def _uuid4_hex() -> str:
    return uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid4_hex)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    query_text: Mapped[str] = mapped_column(String(255), nullable=False)
    platforms: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    timeframe: Mapped[str] = mapped_column(String(32), nullable=False)
    minimum_virality_score: Mapped[float] = mapped_column(nullable=False, default=50.0)
    result_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    format_filters: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    cadence: Mapped[str] = mapped_column(String(32), nullable=False, default="weekly")
    delivery_channels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    delivery_destination: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    runs: Mapped[list[ReportRun]] = relationship(
        back_populates="scheduled_report",
        cascade="all, delete-orphan",
        order_by="ReportRun.created_at.desc()",
    )
    workspace: Mapped["Workspace"] = relationship(back_populates="scheduled_reports")
    user: Mapped["User"] = relationship()


class ReportRun(Base):
    __tablename__ = "report_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_run_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=_uuid4_hex
    )
    scheduled_report_id: Mapped[int] = mapped_column(ForeignKey("scheduled_reports.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    triggered_by: Mapped[str] = mapped_column(String(32), nullable=False, default="scheduled")
    total_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_ranked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    partial_failures: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    pattern_summary: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    pattern_deltas: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    top_clips_snapshot: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    report_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    scheduled_report: Mapped[ScheduledReport] = relationship(back_populates="runs")
    deliveries: Mapped[list[ReportDelivery]] = relationship(
        back_populates="report_run",
        cascade="all, delete-orphan",
        order_by="ReportDelivery.created_at.asc()",
    )
