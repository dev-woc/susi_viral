from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PlatformName(str, Enum):
    tiktok = "tiktok"
    youtube_shorts = "youtube_shorts"


class PatternTagData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    category: str | None = None


class ContentDNAData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schema_version: str = "1.0"
    clip_id: str
    source_url: str
    platform: PlatformName
    virality_score: float = Field(ge=0.0, le=100.0)
    posted_at: datetime | None = None
    niche: str | None = None
    hook: str | None = None
    format: str | None = None
    emotion: str | None = None
    structure: str | None = None
    cta: str | None = None
    replication_notes: str | None = None
    pattern_tags: list[PatternTagData] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ContentDNARead(ContentDNAData):
    id: int
    raw_clip_id: int
    created_at: datetime

