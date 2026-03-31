from __future__ import annotations

from dataclasses import dataclass
from math import log10

from app.schemas.search import Timeframe
from app.services.connectors.base import NormalizedClip, recency_score, score_engagement


@dataclass(slots=True)
class RankedClip:
    clip: NormalizedClip
    normalized_score: float
    rank: int


class ViralityRanker:
    def __init__(self, threshold: float = 50.0) -> None:
        self.threshold = threshold

    def score_clip(self, clip: NormalizedClip, timeframe: Timeframe) -> float:
        views_component = min(log10(max(clip.view_count, 1) + 1) / 6.5, 1.0)
        engagement_component = min(score_engagement(clip) * 6.0, 1.0)
        recency_component = recency_score(clip.posted_at, timeframe.days)
        platform_weight = 1.0 if clip.platform.value == "tiktok" else 0.95
        score = (0.52 * views_component + 0.28 * engagement_component + 0.20 * recency_component) * 100
        return round(score * platform_weight, 2)

    def rank(
        self,
        clips: list[NormalizedClip],
        *,
        timeframe: Timeframe,
        threshold: float | None = None,
        limit: int = 10,
    ) -> list[RankedClip]:
        minimum = self.threshold if threshold is None else threshold
        scored = [
            RankedClip(clip=clip, normalized_score=self.score_clip(clip, timeframe=timeframe), rank=0)
            for clip in clips
        ]
        filtered = [entry for entry in scored if entry.normalized_score >= minimum]
        filtered.sort(key=lambda entry: entry.normalized_score, reverse=True)
        for index, entry in enumerate(filtered[:limit], start=1):
            entry.rank = index
        return filtered[:limit]
