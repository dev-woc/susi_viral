from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid4_hex() -> str:
    return uuid4().hex


class EmbeddingJob(Base):
    __tablename__ = "embedding_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid4_hex)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), index=True)
    content_dna_id: Mapped[int] = mapped_column(ForeignKey("content_dna.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="deterministic-local")
    vector_size: Mapped[int] = mapped_column(Integer, nullable=False, default=16)
    vector_payload: Mapped[list[float]] = mapped_column(JSON, nullable=False, default=list)
    job_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
