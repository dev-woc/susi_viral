from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.library import LibraryItemRead


def _slugify(value: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "collection"


class CollectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    name: str
    slug: str
    description: str | None = None
    created_at: datetime
    item_count: int = 0


class CollectionItemCreateRequest(BaseModel):
    content_dna_id: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=1000)


class CollectionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    content_dna_id: int
    note: str | None = None
    created_at: datetime
    library_item: LibraryItemRead


class CollectionDetailResponse(BaseModel):
    collection: CollectionRead
    items: list[CollectionItemRead] = Field(default_factory=list)


class LibrarySearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default=None, max_length=32)
    hook: str | None = Field(default=None, max_length=255)
    format: str | None = Field(default=None, max_length=255)
    pattern_tag: str | None = Field(default=None, max_length=255)
    collection_id: int | None = Field(default=None, gt=0)
    limit: int = Field(default=25, ge=1, le=100)


class LibrarySearchResponse(BaseModel):
    items: list[LibraryItemRead] = Field(default_factory=list)
    total: int = 0
