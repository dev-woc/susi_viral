from __future__ import annotations

import asyncio

from app.schemas.search import Timeframe
from app.services.connectors.base import ConnectorContext
from app.services.connectors.tiktok import TikTokConnector
from app.services.connectors.youtube_shorts import YouTubeShortsConnector


def test_mock_connectors_are_deterministic() -> None:
    context = ConnectorContext(
        search_id="search-1",
        query="ai marketing",
        timeframe=Timeframe.week_1,
        result_limit=4,
    )

    async def run() -> tuple[list[str], list[str]]:
        tiktok = TikTokConnector(clip_limit=4)
        youtube = YouTubeShortsConnector(clip_limit=4)
        tiktok_result = await tiktok.fetch(context)
        youtube_result = await youtube.fetch(context)
        return (
            [clip.platform_clip_id for clip in tiktok_result.clips],
            [clip.platform_clip_id for clip in youtube_result.clips],
        )

    first = asyncio.run(run())
    second = asyncio.run(run())
    assert first == second
    assert len(first[0]) == 4
    assert len(first[1]) == 4
