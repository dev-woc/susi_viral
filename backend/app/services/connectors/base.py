from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_dna import PlatformName
from app.schemas.search import Timeframe


class ConnectorFailure(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: PlatformName
    stage: str
    message: str
    retryable: bool = True


class ConnectorContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    search_id: str
    query: str
    timeframe: Timeframe
    result_limit: int
    format_filters: list[str] = Field(default_factory=list)


class NormalizedClip(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: PlatformName
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


class ConnectorResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform: PlatformName
    clips: list[NormalizedClip] = Field(default_factory=list)
    failure: ConnectorFailure | None = None


def stable_seed(*parts: str) -> int:
    digest = sha256("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def build_mock_clips(
    *,
    platform: PlatformName,
    context: ConnectorContext,
    variant: str,
    clip_limit: int,
) -> list[NormalizedClip]:
    seed = stable_seed(platform.value, context.query, context.timeframe.value, variant)
    base_time = datetime.now(UTC) - timedelta(hours=seed % (context.timeframe.days * 24 + 1))
    topical_terms = [term for term in context.query.replace("#", " ").split() if term]
    niche = topical_terms[0].lower() if topical_terms else "creator"
    format_cycle = ["listicle", "before_after", "tutorial", "storytime", "screen_recording"]
    emotion_cycle = ["curiosity", "urgency", "delight", "confidence", "surprise"]
    clips: list[NormalizedClip] = []

    for index in range(min(context.result_limit, clip_limit)):
        offset = index + 1
        view_count = 15_000 + (clip_limit - index) * 5_000 + (seed % 3_000)
        like_count = max(300, view_count // (7 + offset))
        comment_count = max(40, view_count // (45 + offset))
        share_count = max(20, view_count // (65 + offset))
        transcript = None if index % 3 == 2 else (
            f"Hook: {context.query} gets a {format_cycle[index % len(format_cycle)]} breakdown "
            f"for {platform.value}. Step {offset} shows why the clip works."
        )
        frame_samples = [f"{platform.value}-{offset}-frame-{frame}" for frame in range(1, 4)]
        clip_id = f"{platform.value}-{seed:x}-{offset}"
        created_at = base_time - timedelta(minutes=index * 17)
        clips.append(
            NormalizedClip(
                platform=platform,
                platform_clip_id=clip_id,
                source_url=f"https://{platform.value}.example.com/watch/{clip_id}",
                title=f"{context.query.title()} - {platform.value} example {offset}",
                description=f"Mock {platform.value} clip about {niche} and {context.query}",
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
                    "format": format_cycle[index % len(format_cycle)],
                    "emotion": emotion_cycle[index % len(emotion_cycle)],
                },
                format_hint=format_cycle[index % len(format_cycle)],
            )
        )
    return clips


def score_engagement(clip: NormalizedClip) -> float:
    numerator = clip.like_count + clip.comment_count * 2 + clip.share_count * 3
    return numerator / max(clip.view_count, 1)


def recency_score(posted_at: datetime | None, window_days: int) -> float:
    if posted_at is None:
        return 0.5
    age_days = max((datetime.now(UTC) - posted_at).total_seconds() / 86_400, 0.0)
    return max(0.0, 1.0 - min(age_days / max(window_days, 1), 1.0))


class PlatformConnector(ABC):
    platform: PlatformName

    @abstractmethod
    async def fetch(self, context: ConnectorContext) -> ConnectorResult:
        raise NotImplementedError

