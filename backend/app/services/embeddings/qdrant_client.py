from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VectorPoint:
    content_dna_id: int
    workspace_id: int
    vector: list[float]
    payload: dict[str, object]


class QdrantClient:
    """Deterministic local stand-in for a vector index."""

    def similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        return max(0.0, min(1.0, sum(a * b for a, b in zip(left, right))))
