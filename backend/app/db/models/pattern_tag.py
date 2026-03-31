from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


content_dna_pattern_tags = Table(
    "content_dna_pattern_tags",
    Base.metadata,
    Column("content_dna_id", ForeignKey("content_dna.id"), primary_key=True),
    Column("pattern_tag_id", ForeignKey("pattern_tags.id"), primary_key=True),
)


class PatternTag(Base):
    __tablename__ = "pattern_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)

    content_dna: Mapped[list["ContentDNA"]] = relationship(
        secondary=content_dna_pattern_tags, back_populates="pattern_tags"
    )
