from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.schemas.content_dna import PlatformName
from app.schemas.search import Timeframe
from app.services.connectors.base import NormalizedClip
from app.services.ranking.virality import ViralityRanker


def test_virality_ranker_sorts_and_filters() -> None:
    ranker = ViralityRanker(threshold=40.0)
    now = datetime.now(UTC)
    clips = [
        NormalizedClip(
            platform=PlatformName.tiktok,
            platform_clip_id="clip-high",
            source_url="https://example.com/high",
            title="High",
            view_count=100_000,
            like_count=15_000,
            comment_count=2_000,
            share_count=1_500,
            posted_at=now - timedelta(hours=2),
        ),
        NormalizedClip(
            platform=PlatformName.youtube_shorts,
            platform_clip_id="clip-low",
            source_url="https://example.com/low",
            title="Low",
            view_count=2_000,
            like_count=50,
            comment_count=10,
            share_count=3,
            posted_at=now - timedelta(days=4),
        ),
    ]

    ranked = ranker.rank(clips, timeframe=Timeframe.week_1, threshold=40.0, limit=10)
    assert [entry.clip.platform_clip_id for entry in ranked] == ["clip-high"]
    assert ranked[0].normalized_score >= 40.0
