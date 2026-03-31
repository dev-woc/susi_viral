from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.search import Timeframe


class ReportPlatform(StrEnum):
    tiktok = "tiktok"
    youtube_shorts = "youtube_shorts"
    instagram_reels = "instagram_reels"
    twitter_x = "twitter_x"
    reddit = "reddit"


class ReportFrequency(StrEnum):
    daily = "daily"
    weekly = "weekly"
    custom = "custom"


class ReportDeliveryChannel(StrEnum):
    email = "email"
    dashboard = "dashboard"
    pdf = "pdf"


class ReportStatus(StrEnum):
    queued = "queued"
    running = "running"
    partial = "partial"
    complete = "complete"
    failed = "failed"


class ReportDeliveryStatus(StrEnum):
    queued = "queued"
    sent = "sent"
    failed = "failed"


class ReportConnectorFailure(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: ReportPlatform
    stage: str
    message: str
    retryable: bool = True


class ReportContentDNAData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schema_version: str = "1.0"
    clip_id: str
    source_url: str
    platform: ReportPlatform
    virality_score: float = Field(ge=0.0, le=100.0)
    posted_at: datetime | None = None
    niche: str | None = None
    hook: str | None = None
    format: str | None = None
    emotion: str | None = None
    structure: str | None = None
    cta: str | None = None
    replication_notes: str | None = None
    pattern_tags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ReportSearchRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    query_text: str = Field(min_length=1, max_length=255)
    platforms: list[ReportPlatform] = Field(default_factory=lambda: [ReportPlatform.tiktok])
    timeframe: Timeframe = Timeframe.week_1
    minimum_virality_score: float = Field(default=50.0, ge=0.0, le=100.0)
    result_limit: int = Field(default=10, ge=1, le=50)
    format_filters: list[str] = Field(default_factory=list)
    cadence: ReportFrequency = ReportFrequency.weekly
    delivery_channels: list[ReportDeliveryChannel] = Field(
        default_factory=lambda: [ReportDeliveryChannel.dashboard]
    )
    delivery_destination: str | None = None
    notes: str | None = None
    enabled: bool = True


class ReportClipResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clip_id: str
    platform: ReportPlatform
    source_url: str
    title: str
    author_handle: str | None = None
    thumbnail_url: str | None = None
    posted_at: datetime | None = None
    virality_score: float
    transcript_excerpt: str | None = None
    content_dna: ReportContentDNAData


class ReportDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    delivery_id: str
    report_run_id: int
    channel: ReportDeliveryChannel
    destination: str | None = None
    status: ReportDeliveryStatus
    retryable: bool = True
    message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class ReportRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_run_id: str
    scheduled_report_id: int
    status: ReportStatus
    triggered_by: str
    total_fetched: int
    total_ranked: int
    partial_failures: list[ReportConnectorFailure] = Field(default_factory=list)
    pattern_summary: dict[str, int] = Field(default_factory=dict)
    pattern_deltas: dict[str, int] = Field(default_factory=dict)
    top_clips: list[ReportClipResult] = Field(default_factory=list)
    deliveries: list[ReportDeliveryRead] = Field(default_factory=list)
    report_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: datetime | None = None


class ScheduledReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: str
    workspace_id: int
    user_id: int
    name: str
    query_text: str
    platforms: list[ReportPlatform]
    timeframe: Timeframe
    minimum_virality_score: float
    result_limit: int
    format_filters: list[str] = Field(default_factory=list)
    cadence: ReportFrequency
    delivery_channels: list[ReportDeliveryChannel] = Field(default_factory=list)
    delivery_destination: str | None = None
    enabled: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    latest_run: ReportRunRead | None = None


class ScheduledReportListResponse(BaseModel):
    items: list[ScheduledReportRead]


class ReportRunListResponse(BaseModel):
    items: list[ReportRunRead]


class ReportExecutionSnapshot(BaseModel):
    report_id: str
    report_run_id: str
    status: ReportStatus
    query_text: str
    timeframe: Timeframe
    minimum_virality_score: float
    result_limit: int
    platforms: list[ReportPlatform]
    total_fetched: int
    total_ranked: int
    partial_failures: list[ReportConnectorFailure] = Field(default_factory=list)
    pattern_summary: dict[str, int] = Field(default_factory=dict)
    pattern_deltas: dict[str, int] = Field(default_factory=dict)
    top_clips: list[ReportClipResult] = Field(default_factory=list)
    deliveries: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    completed_at: datetime | None = None
