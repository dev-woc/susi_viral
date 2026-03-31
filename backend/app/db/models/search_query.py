from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    query_text: Mapped[str] = mapped_column(String(255), nullable=False)
    platforms: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    timeframe: Mapped[str] = mapped_column(String(32), nullable=False)
    min_virality_score: Mapped[float] = mapped_column(nullable=False, default=50.0)
    result_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    partial_failures: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    pattern_summary: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    search_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="search_queries")
    user: Mapped["User"] = relationship(back_populates="search_queries")
    raw_clips: Mapped[list["RawClip"]] = relationship(
        back_populates="search_query", cascade="all, delete-orphan"
    )
