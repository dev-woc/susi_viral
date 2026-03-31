from __future__ import annotations

import asyncio

from app.core.config import Settings
from app.schemas.content_dna import PlatformName
from app.services.connectors.base import NormalizedClip
from app.services.extraction.content_dna_extractor import ContentDNAExtractor


def test_fallback_content_dna_extraction_is_stable() -> None:
    extractor = ContentDNAExtractor(Settings())
    clip = NormalizedClip(
        platform=PlatformName.tiktok,
        platform_clip_id="clip-123",
        source_url="https://example.com/clip-123",
        title="How to make a better hook in 10 seconds",
        description="A quick walkthrough for creators",
        transcript=None,
        frame_samples=["frame-1", "frame-2"],
        view_count=50_000,
        like_count=5_000,
        comment_count=200,
        share_count=100,
    )

    async def run() -> str:
        payload = await extractor.extract(clip, 81.5)
        assert payload.clip_id == "clip-123"
        assert payload.platform == PlatformName.tiktok
        assert payload.pattern_tags
        assert payload.confidence > 0.0
        return payload.model_dump_json()

    first = asyncio.run(run())
    second = asyncio.run(run())
    assert first == second
