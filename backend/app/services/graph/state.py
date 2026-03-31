from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.search import ConnectorFailure, SearchRequest, SearchStatus
from app.services.connectors.base import NormalizedClip
from app.services.ranking.virality import RankedClip


@dataclass(slots=True)
class SearchState:
    search_id: str
    request: SearchRequest
    workspace_id: int
    user_id: int
    fetched_clips: list[NormalizedClip] = field(default_factory=list)
    failures: list[ConnectorFailure] = field(default_factory=list)
    ranked_clips: list[RankedClip] = field(default_factory=list)
    extracted_payloads: dict[str, object] = field(default_factory=dict)
    pattern_counts: dict[str, int] = field(default_factory=dict)
    status: SearchStatus = SearchStatus.pending

