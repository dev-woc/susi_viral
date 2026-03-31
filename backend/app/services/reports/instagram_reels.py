from __future__ import annotations

from app.schemas.report import ReportPlatform
from app.services.reports.base import (
    ReportConnector,
    ReportConnectorContext,
    ReportConnectorResult,
    build_mock_clips,
)


class InstagramReelsConnector(ReportConnector):
    platform = ReportPlatform.instagram_reels

    def __init__(self, clip_limit: int = 6) -> None:
        self.clip_limit = clip_limit

    async def fetch(self, context: ReportConnectorContext) -> ReportConnectorResult:
        if "fail-instagram" in context.query_text.lower():
            raise RuntimeError("Instagram Reels connector simulated an upstream failure")

        clips = build_mock_clips(
            platform=self.platform,
            context=context,
            variant="instagram-reels-mock",
            clip_limit=self.clip_limit,
        )
        return ReportConnectorResult(
            platform=self.platform, clips=clips, total_available=len(clips)
        )
