from __future__ import annotations

import asyncio

from app.schemas.content_dna import PlatformName
from app.schemas.search import SearchRequest, Timeframe
from app.services.connectors.base import ConnectorContext
from app.services.identity import RequestIdentity


class FailingConnector:
    async def fetch(self, context: ConnectorContext):  # type: ignore[no-untyped-def]
        raise RuntimeError("simulated platform failure")


def test_search_survives_partial_platform_failure(app) -> None:
    service = app.state.search_service
    service.graph.connectors[PlatformName.youtube_shorts] = FailingConnector()
    request = SearchRequest(
        query="test failure handling",
        platforms=[PlatformName.tiktok, PlatformName.youtube_shorts],
        timeframe=Timeframe.week_1,
        minimum_virality_score=10.0,
        result_limit=5,
    )
    identity = RequestIdentity(
        workspace_id=app.state.default_workspace.id,
        user_id=app.state.default_user.id,
        workspace_slug=app.state.default_workspace.slug,
        user_external_id=app.state.default_user.external_id,
    )

    result = asyncio.run(service.run_search(request, identity))
    assert result.status in {"partial", "failed"}
    assert result.platform_failures
    assert any(failure.platform == PlatformName.youtube_shorts for failure in result.platform_failures)
