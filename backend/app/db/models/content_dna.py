from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContentDNA(Base):
    __tablename__ = "content_dna"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_clip_id: Mapped[int] = mapped_column(ForeignKey("raw_clips.id"), unique=True, index=True)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    clip_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    virality_score: Mapped[float] = mapped_column(nullable=False, default=0.0)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    niche: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    format: Mapped[str | None] = mapped_column(String(120), nullable=True)
    emotion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    structure: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    replication_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)
    extracted_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    raw_clip: Mapped["RawClip"] = relationship(back_populates="content_dna")
    pattern_tags: Mapped[list["PatternTag"]] = relationship(
        secondary="content_dna_pattern_tags", back_populates="content_dna"
    )
