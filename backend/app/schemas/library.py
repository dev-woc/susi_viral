from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content_dna import ContentDNARead
from app.schemas.search import RawClipRead


class LibraryItemCreate(BaseModel):
    content_dna_id: int = Field(gt=0)
    note: str | None = None


class LibraryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    content_dna_id: int
    note: str | None = None
    created_at: datetime
    content_dna: ContentDNARead
    raw_clip: RawClipRead

