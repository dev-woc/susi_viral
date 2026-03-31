from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="workspace")
    search_queries: Mapped[list["SearchQuery"]] = relationship(back_populates="workspace")
    library_items: Mapped[list["LibraryItem"]] = relationship(back_populates="workspace")
    collections: Mapped[list["Collection"]] = relationship(back_populates="workspace")
    scheduled_reports: Mapped[list["ScheduledReport"]] = relationship(back_populates="workspace")
