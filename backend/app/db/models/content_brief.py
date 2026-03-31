from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid4_hex() -> str:
    return uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ContentBrief(Base):
    __tablename__ = "content_briefs"

    id: Mapped[int] = mapped_column(primary_key=True)
    brief_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=_uuid4_hex, nullable=False
    )
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    report_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("report_runs.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[str] = mapped_column(Text(), nullable=False)
    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    tone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    summary: Mapped[str] = mapped_column(Text(), nullable=False)
    recommended_shots: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    selected_content_dna_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    pattern_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    prompt_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    source_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
