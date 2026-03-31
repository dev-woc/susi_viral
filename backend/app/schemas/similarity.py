from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_dna import ContentDNARead, PlatformName


class SimilaritySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)
    platform: PlatformName | None = None
    collection_id: int | None = Field(default=None, gt=0)


class SimilarityResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_dna_id: int
    score: float = Field(ge=0.0, le=1.0)
    matched_on: str
    content_dna: ContentDNARead


class SimilaritySearchResponse(BaseModel):
    items: list[SimilarityResultRead] = Field(default_factory=list)
    query: str
    provider: str
    generated_at: datetime
