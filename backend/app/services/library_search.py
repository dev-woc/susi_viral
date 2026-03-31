from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.bootstrap import ensure_default_workspace
from app.db.models.collection import Collection
from app.db.models.collection_item import CollectionItem
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.pattern_tag import PatternTag, content_dna_pattern_tags
from app.db.models.raw_clip import RawClip
from app.schemas.collection import (
    CollectionCreateRequest,
    CollectionDetailResponse,
    CollectionItemCreateRequest,
    CollectionItemRead,
    CollectionRead,
    LibrarySearchRequest,
    LibrarySearchResponse,
)
from app.schemas.content_dna import ContentDNARead, PatternTagData, PlatformName
from app.schemas.library import LibraryItemRead
from app.schemas.search import RawClipRead


@dataclass(slots=True)
class LibrarySearchFilters:
    query: str | None = None
    platform: str | None = None
    hook: str | None = None
    format: str | None = None
    pattern_tag: str | None = None
    collection_id: int | None = None
    limit: int = 25


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "collection"


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token]


class LibrarySearchService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search_library(self, session: Session, filters: LibrarySearchFilters) -> LibrarySearchResponse:
        workspace = ensure_default_workspace(session, self.settings)
        query = (
            select(LibraryItem)
            .join(LibraryItem.content_dna)
            .join(ContentDNA.raw_clip)
            .options(
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.pattern_tags),
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.raw_clip),
            )
            .where(LibraryItem.workspace_id == workspace.id)
        )

        if filters.platform:
            query = query.where(ContentDNA.platform == filters.platform)
        if filters.hook:
            query = query.where(func.lower(ContentDNA.hook).like(f"%{filters.hook.lower()}%"))
        if filters.format:
            query = query.where(func.lower(ContentDNA.format).like(f"%{filters.format.lower()}%"))
        if filters.collection_id is not None:
            collection_membership = exists(
                select(1).where(
                    CollectionItem.collection_id == filters.collection_id,
                    CollectionItem.content_dna_id == LibraryItem.content_dna_id,
                )
            )
            query = query.where(collection_membership)

        if filters.pattern_tag:
            tag_match = exists(
                select(1)
                .select_from(content_dna_pattern_tags.join(PatternTag))
                .where(
                    content_dna_pattern_tags.c.content_dna_id == ContentDNA.id,
                    or_(
                        func.lower(PatternTag.name).like(f"%{filters.pattern_tag.lower()}%"),
                        func.lower(PatternTag.category).like(f"%{filters.pattern_tag.lower()}%"),
                    ),
                )
            )
            query = query.where(tag_match)

        if filters.query:
            terms = _tokenize(filters.query)
            searchable_fields = [
                LibraryItem.note,
                ContentDNA.niche,
                ContentDNA.hook,
                ContentDNA.format,
                ContentDNA.emotion,
                ContentDNA.structure,
                ContentDNA.cta,
                ContentDNA.replication_notes,
                RawClip.title,
                RawClip.description,
                RawClip.transcript,
                RawClip.author_name,
                RawClip.author_handle,
            ]

            for term in terms:
                term_filter = or_(
                    *[func.lower(field).like(f"%{term}%") for field in searchable_fields],
                    exists(
                        select(1)
                        .select_from(content_dna_pattern_tags.join(PatternTag))
                        .where(
                            content_dna_pattern_tags.c.content_dna_id == ContentDNA.id,
                            or_(
                                func.lower(PatternTag.name).like(f"%{term}%"),
                                func.lower(PatternTag.category).like(f"%{term}%"),
                            ),
                        )
                    ),
                )
                query = query.where(term_filter)

        query = (
            query.order_by(LibraryItem.created_at.desc(), ContentDNA.virality_score.desc())
            .limit(filters.limit)
        )
        items = list(session.scalars(query).unique())
        return LibrarySearchResponse(items=[self._library_item_read(item) for item in items], total=len(items))

    def create_collection(
        self, session: Session, payload: CollectionCreateRequest
    ) -> CollectionRead:
        workspace = ensure_default_workspace(session, self.settings)
        slug = payload.slug or _slugify(payload.name)
        collection = session.scalar(
            select(Collection).where(
                Collection.workspace_id == workspace.id,
                Collection.slug == slug,
            )
        )
        if collection is None:
            collection = Collection(
                workspace_id=workspace.id,
                name=payload.name,
                slug=slug,
                description=payload.description,
            )
            session.add(collection)
            session.commit()
            session.refresh(collection)
        return self._collection_read(session, collection)

    def list_collections(self, session: Session) -> list[CollectionRead]:
        workspace = ensure_default_workspace(session, self.settings)
        collections = list(
            session.scalars(
                select(Collection)
                .where(Collection.workspace_id == workspace.id)
                .order_by(Collection.created_at.desc())
            )
        )
        return [self._collection_read(session, collection) for collection in collections]

    def get_collection(self, session: Session, collection_id: int) -> CollectionDetailResponse | None:
        collection = session.get(Collection, collection_id)
        if collection is None:
            return None
        workspace = ensure_default_workspace(session, self.settings)
        if collection.workspace_id != workspace.id:
            return None

        items = list(
            session.scalars(
                select(CollectionItem)
                .where(CollectionItem.collection_id == collection.id)
                .options(selectinload(CollectionItem.content_dna).selectinload(ContentDNA.raw_clip))
                .order_by(CollectionItem.created_at.desc())
            )
        )
        return CollectionDetailResponse(
            collection=self._collection_read(session, collection),
            items=[self._collection_item_read(session, item) for item in items],
        )

    def add_item_to_collection(
        self,
        session: Session,
        collection_id: int,
        payload: CollectionItemCreateRequest,
    ) -> CollectionItemRead:
        collection = session.get(Collection, collection_id)
        if collection is None:
            raise LookupError(f"collection_id {collection_id} not found")

        workspace = ensure_default_workspace(session, self.settings)
        if collection.workspace_id != workspace.id:
            raise LookupError(f"collection_id {collection_id} not found")

        content_dna = session.get(ContentDNA, payload.content_dna_id)
        if content_dna is None:
            raise LookupError(f"content_dna_id {payload.content_dna_id} not found")

        library_item = self._library_item_for_content_dna(session, workspace.id, content_dna.id)
        if library_item is None:
            raise LookupError(
                f"content_dna_id {payload.content_dna_id} is not available in the workspace library"
            )

        item = session.scalar(
            select(CollectionItem).where(
                CollectionItem.collection_id == collection.id,
                CollectionItem.content_dna_id == content_dna.id,
            )
        )
        if item is None:
            item = CollectionItem(
                collection_id=collection.id,
                content_dna_id=content_dna.id,
                note=payload.note,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
        else:
            if payload.note is not None and item.note != payload.note:
                item.note = payload.note
                session.commit()

        return self._collection_item_read(session, item)

    def search_request(self, session: Session, payload: LibrarySearchRequest) -> LibrarySearchResponse:
        return self.search_library(
            session,
            LibrarySearchFilters(
                query=payload.query,
                platform=payload.platform,
                hook=payload.hook,
                format=payload.format,
                pattern_tag=payload.pattern_tag,
                collection_id=payload.collection_id,
                limit=payload.limit,
            ),
        )

    def _collection_read(self, session: Session, collection: Collection) -> CollectionRead:
        item_count = session.scalar(
            select(func.count(CollectionItem.id)).where(CollectionItem.collection_id == collection.id)
        )
        return CollectionRead(
            id=collection.id,
            workspace_id=collection.workspace_id,
            name=collection.name,
            slug=collection.slug,
            description=collection.description,
            created_at=collection.created_at,
            item_count=int(item_count or 0),
        )

    def _collection_item_read(self, session: Session, item: CollectionItem) -> CollectionItemRead:
        library_item = self._library_item_for_content_dna(
            session,
            ensure_default_workspace(session, self.settings).id,
            item.content_dna_id,
        )
        if library_item is None:
            raise LookupError(f"content_dna_id {item.content_dna_id} not found in library")
        return CollectionItemRead(
            id=item.id,
            collection_id=item.collection_id,
            content_dna_id=item.content_dna_id,
            note=item.note,
            created_at=item.created_at,
            library_item=self._library_item_read(library_item),
        )

    def _library_item_for_content_dna(
        self, session: Session, workspace_id: int, content_dna_id: int
    ) -> LibraryItem | None:
        return session.scalar(
            select(LibraryItem)
            .where(
                LibraryItem.workspace_id == workspace_id,
                LibraryItem.content_dna_id == content_dna_id,
            )
            .options(
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.raw_clip),
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.pattern_tags),
            )
        )

    def _library_item_read(self, item: LibraryItem) -> LibraryItemRead:
        assert item.content_dna is not None
        raw_clip = item.content_dna.raw_clip
        assert raw_clip is not None
        return LibraryItemRead(
            id=item.id,
            workspace_id=item.workspace_id,
            content_dna_id=item.content_dna_id,
            note=item.note,
            created_at=item.created_at,
            content_dna=ContentDNARead(
                id=item.content_dna.id,
                raw_clip_id=item.content_dna.raw_clip_id,
                schema_version=item.content_dna.schema_version,
                clip_id=item.content_dna.clip_id,
                source_url=item.content_dna.source_url,
                platform=PlatformName(item.content_dna.platform),
                virality_score=item.content_dna.virality_score,
                posted_at=item.content_dna.posted_at,
                niche=item.content_dna.niche,
                hook=item.content_dna.hook,
                format=item.content_dna.format,
                emotion=item.content_dna.emotion,
                structure=item.content_dna.structure,
                cta=item.content_dna.cta,
                replication_notes=item.content_dna.replication_notes,
                pattern_tags=[
                    PatternTagData(name=tag.name, category=tag.category)
                    for tag in item.content_dna.pattern_tags
                ],
                confidence=item.content_dna.confidence,
                created_at=item.content_dna.created_at,
            ),
            raw_clip=RawClipRead(
                id=raw_clip.id,
                search_query_id=raw_clip.search_query_id,
                platform=PlatformName(raw_clip.platform),
                platform_clip_id=raw_clip.platform_clip_id,
                source_url=raw_clip.source_url,
                title=raw_clip.title,
                description=raw_clip.description,
                author_name=raw_clip.author_name,
                author_handle=raw_clip.author_handle,
                view_count=raw_clip.view_count,
                like_count=raw_clip.like_count,
                comment_count=raw_clip.comment_count,
                share_count=raw_clip.share_count,
                posted_at=raw_clip.posted_at,
                transcript=raw_clip.transcript,
                frame_samples=list(raw_clip.frame_samples or []),
                raw_payload=dict(raw_clip.raw_payload or {}),
                normalized_score=raw_clip.normalized_score,
                rank=raw_clip.rank,
                content_dna=None,
            ),
        )


@lru_cache(maxsize=1)
def get_library_search_service() -> LibrarySearchService:
    return LibrarySearchService()
