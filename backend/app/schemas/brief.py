from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_dna import ContentDNARead


class ContentBriefCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    objective: str = Field(min_length=1, max_length=1000)
    audience: str = Field(min_length=1, max_length=255)
    selected_content_dna_ids: list[int] = Field(default_factory=list, min_length=1)
    report_run_id: int | None = Field(default=None, gt=0)
    tone: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=1000)


class ContentBriefRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brief_id: str
    workspace_id: int
    user_id: int
    report_run_id: int | None = None
    title: str
    objective: str
    audience: str
    tone: str | None = None
    summary: str
    recommended_shots: list[str] = Field(default_factory=list)
    selected_content_dna_ids: list[int] = Field(default_factory=list)
    pattern_tags: list[str] = Field(default_factory=list)
    prompt_snapshot: dict[str, Any] = Field(default_factory=dict)
    source_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    selected_clips: list[ContentDNARead] = Field(default_factory=list)


class ContentBriefListResponse(BaseModel):
    items: list[ContentBriefRead] = Field(default_factory=list)
