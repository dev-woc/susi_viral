from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RequestIdentity:
    workspace_id: int
    user_id: int
    workspace_slug: str
    user_external_id: str
