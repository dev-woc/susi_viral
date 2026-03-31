from __future__ import annotations

import logging

from app.schemas.content_dna import PlatformName
from app.services.connectors.base import ConnectorContext, ConnectorResult, build_mock_clips


class TikTokConnector:
    platform = PlatformName.tiktok

    def __init__(self, clip_limit: int = 6) -> None:
        self.clip_limit = clip_limit
        self.logger = logging.getLogger(__name__)

    async def fetch(self, context: ConnectorContext) -> ConnectorResult:
        self.logger.info(
            "fetching tiktok clips",
            extra={"search_id": context.search_id, "platform": self.platform.value, "stage": "fetch"},
        )
        clips = build_mock_clips(
            platform=self.platform,
            context=context,
            variant="tiktok-mock",
            clip_limit=self.clip_limit,
        )
        return ConnectorResult(platform=self.platform, clips=clips)

