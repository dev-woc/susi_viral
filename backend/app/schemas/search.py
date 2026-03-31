from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_dna import ContentDNARead, PlatformName


class Timeframe(str, Enum):
    day_1 = "24h"
    week_1 = "7d"
    month_1 = "30d"

    @property
    def days(self) -> int:
        if self is Timeframe.day_1:
            return 1
        if self is Timeframe.week_1:
            return 7
        return 30


class SearchStatus(str, Enum):
    pending = "pending"
    partial = "partial"
    completed = "completed"
    failed = "failed"


class ConnectorFailure(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: PlatformName
    stage: str
    message: str
    retryable: bool = True


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=255)
    platforms: list[PlatformName] = Field(
        default_factory=lambda: [PlatformName.tiktok, PlatformName.youtube_shorts]
    )
    timeframe: Timeframe = Timeframe.week_1
    minimum_virality_score: float = Field(default=50.0, ge=0.0, le=100.0)
    format_filters: list[str] = Field(default_factory=list)
    result_limit: int | None = Field(default=None, ge=1, le=50)


class RawClipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_query_id: int
    platform: PlatformName
    platform_clip_id: str
    source_url: str
    title: str
    description: str | None = None
    author_name: str | None = None
    author_handle: str | None = None
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    posted_at: datetime | None = None
    transcript: str | None = None
    frame_samples: list[str] = Field(default_factory=list)
    raw_payload: dict[str, object] = Field(default_factory=dict)
    normalized_score: float = 0.0
    rank: int | None = None
    content_dna: ContentDNARead | None = None


class RankedSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_clip: RawClipRead
    content_dna: ContentDNARead | None = None
    rank: int
    normalized_score: float


class SearchSummary(BaseModel):
    total_fetched: int = 0
    total_ranked: int = 0
    total_saved: int = 0
    pattern_counts: dict[str, int] = Field(default_factory=dict)


class SearchDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    search_id: str
    status: SearchStatus
    query: str
    timeframe: Timeframe
    minimum_virality_score: float
    result_limit: int
    platforms: list[PlatformName]
    created_at: datetime
    completed_at: datetime | None = None
    results: list[RankedSearchResult] = Field(default_factory=list)
    platform_failures: list[ConnectorFailure] = Field(default_factory=list)
    summary: SearchSummary = Field(default_factory=SearchSummary)

