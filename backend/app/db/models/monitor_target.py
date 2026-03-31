from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid4_hex() -> str:
    return uuid4().hex


class MonitorTarget(Base):
    __tablename__ = "monitor_targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=_uuid4_hex, nullable=False
    )
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    account_handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    query_text: Mapped[str] = mapped_column(Text(), nullable=False)
    cadence: Mapped[str] = mapped_column(String(32), nullable=False, default="weekly")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
