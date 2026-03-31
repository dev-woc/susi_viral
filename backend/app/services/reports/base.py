from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from math import log10
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.report import (
    ReportDeliveryChannel,
    ReportDeliveryStatus,
    ReportPlatform,
)
from app.schemas.search import Timeframe


class ReportConnectorFailure(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: ReportPlatform
    stage: str
    message: str
    retryable: bool = True


class ReportConnectorContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scheduled_report_id: int
    report_run_id: str
    query_text: str
    timeframe: Timeframe
    result_limit: int
    format_filters: list[str] = Field(default_factory=list)


class ReportNormalizedClip(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: ReportPlatform
    platform_clip_id: str
    source_url: str
    title: str
    description: str | None = None
    author_name: str | None = None
    author_handle: str | None = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    posted_at: datetime | None = None
    transcript: str | None = None
    frame_samples: list[str] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    format_hint: str | None = None


class ReportConnectorResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: ReportPlatform
    clips: list[ReportNormalizedClip] = Field(default_factory=list)
    total_available: int = 0
    failure: ReportConnectorFailure | None = None


class ReportPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scheduled_report_id: int
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
    cadence: str
    delivery_channels: list[ReportDeliveryChannel] = Field(default_factory=list)
    delivery_destination: str | None = None
    notes: str | None = None
    enabled: bool = True


class ReportDeliveryOutcome(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel: ReportDeliveryChannel
    destination: str | None = None
    status: ReportDeliveryStatus
    retryable: bool = True
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ReportExecutionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    total_fetched: int
    total_ranked: int
    partial_failures: list[ReportConnectorFailure] = Field(default_factory=list)
    pattern_summary: dict[str, int] = Field(default_factory=dict)
    pattern_deltas: dict[str, int] = Field(default_factory=dict)
    top_clips: list[dict[str, Any]] = Field(default_factory=list)
    deliveries: list[ReportDeliveryOutcome] = Field(default_factory=list)
    report_snapshot: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime | None = None


class ReportConnector(ABC):
    platform: ReportPlatform

    @abstractmethod
    async def fetch(self, context: ReportConnectorContext) -> ReportConnectorResult:
        raise NotImplementedError


def stable_seed(*parts: str) -> int:
    digest = sha256("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def build_mock_clips(
    *,
    platform: ReportPlatform,
    context: ReportConnectorContext,
    variant: str,
    clip_limit: int,
) -> list[ReportNormalizedClip]:
    seed = stable_seed(
        platform.value,
        context.query_text,
        context.timeframe.value,
        context.report_run_id,
        variant,
    )
    base_time = datetime.now(UTC) - timedelta(hours=seed % (context.timeframe.days * 24 + 1))
    topical_terms = [term for term in context.query_text.replace("#", " ").split() if term]
    niche = topical_terms[0].lower() if topical_terms else "creator"
    format_cycle = ["listicle", "before_after", "tutorial", "storytime", "screen_recording"]
    emotion_cycle = ["curiosity", "urgency", "delight", "confidence", "surprise"]
    clips: list[ReportNormalizedClip] = []

    for index in range(min(context.result_limit, clip_limit)):
        offset = index + 1
        format_name = format_cycle[index % len(format_cycle)]
        view_count = 16_000 + (clip_limit - index) * 5_250 + (seed % 2_500)
        like_count = max(300, view_count // (7 + offset))
        comment_count = max(40, view_count // (45 + offset))
        share_count = max(20, view_count // (65 + offset))
        transcript = (
            None
            if index % 3 == 2
            else (
                f"Hook: {context.query_text} gets a {format_name} breakdown "
                f"for {platform.value}. Step {offset} shows why the clip works."
            )
        )
        frame_samples = [f"{platform.value}-{offset}-frame-{frame}" for frame in range(1, 4)]
        clip_id = f"{platform.value}-{seed:x}-{offset}"
        created_at = base_time - timedelta(minutes=index * 17)
        clips.append(
            ReportNormalizedClip(
                platform=platform,
                platform_clip_id=clip_id,
                source_url=f"https://{platform.value}.example.com/watch/{clip_id}",
                title=f"{context.query_text.title()} - {platform.value} example {offset}",
                description=f"Mock {platform.value} clip about {niche} and {context.query_text}",
                author_name=f"{platform.value.title()} Creator {offset}",
                author_handle=f"@{platform.value}_{offset}",
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                share_count=share_count,
                posted_at=created_at,
                transcript=transcript,
                frame_samples=frame_samples,
                raw_payload={
                    "seed": seed,
                    "platform": platform.value,
                    "variant": variant,
                    "index": index,
                    "niche": niche,
                    "format": format_name,
                    "emotion": emotion_cycle[index % len(emotion_cycle)],
                },
                format_hint=format_name,
            )
        )
    return clips


def score_engagement(clip: ReportNormalizedClip) -> float:
    numerator = clip.like_count + clip.comment_count * 2 + clip.share_count * 3
    return numerator / max(clip.view_count, 1)


def recency_score(posted_at: datetime | None, window_days: int) -> float:
    if posted_at is None:
        return 0.5
    age_days = max((datetime.now(UTC) - posted_at).total_seconds() / 86_400, 0.0)
    return max(0.0, 1.0 - min(age_days / max(window_days, 1), 1.0))


def score_clip(clip: ReportNormalizedClip, timeframe: Timeframe) -> float:
    views_component = min(log10(max(clip.view_count, 1) + 1) / 5.0, 1.0)
    engagement_component = min(score_engagement(clip) * 6.0, 1.0)
    recency_component = recency_score(clip.posted_at, timeframe.days)
    platform_weight = {
        ReportPlatform.tiktok: 1.0,
        ReportPlatform.youtube_shorts: 0.95,
        ReportPlatform.instagram_reels: 0.93,
        ReportPlatform.twitter_x: 0.88,
        ReportPlatform.reddit: 0.9,
    }[clip.platform]
    score = (0.52 * views_component + 0.28 * engagement_component + 0.20 * recency_component) * 100
    return round(score * platform_weight, 2)
