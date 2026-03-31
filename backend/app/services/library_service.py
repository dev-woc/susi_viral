from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.bootstrap import ensure_default_user, ensure_default_workspace
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery
from app.schemas.content_dna import ContentDNAResponse
from app.schemas.library import LibraryItemResponse, LibraryListResponse, SaveLibraryItemRequest
from app.schemas.search import SearchRequest, SearchResult
from app.services.shared import build_search_result_from_content_dna, get_settings


class LibraryService:
    def save_item(self, session: Session, payload: SaveLibraryItemRequest) -> LibraryItemResponse:
        settings = get_settings()
        workspace = ensure_default_workspace(session, settings)
        ensure_default_user(session, settings, workspace)

        content_dna = session.scalar(
            select(ContentDNA)
            .join(RawClip)
            .join(SearchQuery)
            .where(SearchQuery.id == payload.search_id, ContentDNA.clip_id == payload.clip.clip_id)
            .options(selectinload(ContentDNA.pattern_tags), selectinload(ContentDNA.raw_clip))
        )
        if content_dna is None:
            content_dna = self._create_standalone_content_dna(session, payload)

        existing = session.scalar(
            select(LibraryItem).where(
                LibraryItem.workspace_id == workspace.id,
                LibraryItem.content_dna_id == content_dna.id,
            )
        )
        if existing is None:
            existing = LibraryItem(
                id=str(uuid4()),
                workspace_id=workspace.id,
                content_dna_id=content_dna.id,
                saved_note=payload.saved_note,
                saved_at=datetime.now(tz=UTC),
            )
            session.add(existing)
            session.commit()
            session.refresh(existing)

        return LibraryItemResponse(
            id=existing.id,
            saved_at=existing.saved_at,
            workspace_id=existing.workspace_id,
            clip=build_search_result_from_content_dna(content_dna),
            saved_note=existing.saved_note,
        )

    def list_items(self, session: Session, platform: str | None, hook: str | None) -> LibraryListResponse:
        settings = get_settings()
        workspace = ensure_default_workspace(session, settings)

        query = (
            select(LibraryItem)
            .where(LibraryItem.workspace_id == workspace.id)
            .options(
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.pattern_tags),
                selectinload(LibraryItem.content_dna).selectinload(ContentDNA.raw_clip),
            )
        )
        items = list(session.scalars(query))

        responses: list[LibraryItemResponse] = []
        for item in items:
            clip = build_search_result_from_content_dna(item.content_dna)
            if platform and clip.platform != platform:
                continue
            if hook and (clip.content_dna.hook or "").lower().find(hook.lower()) == -1:
                continue
            responses.append(
                LibraryItemResponse(
                    id=item.id,
                    saved_at=item.saved_at,
                    workspace_id=item.workspace_id,
                    clip=clip,
                    saved_note=item.saved_note,
                )
            )
        return LibraryListResponse(items=responses)

    def _create_standalone_content_dna(
        self,
        session: Session,
        payload: SaveLibraryItemRequest,
    ) -> ContentDNA:
        settings = get_settings()
        workspace = ensure_default_workspace(session, settings)
        search = SearchQuery(
            id=payload.search_id,
            workspace_id=workspace.id,
            query_text=payload.clip.content_dna.niche or "manual save",
            timeframe="7d",
            virality_threshold=0,
            platforms=[payload.clip.platform],
            format_filters=[],
            status="complete",
            partial_failures=[],
            total_available=1,
            created_at=datetime.now(tz=UTC),
        )
        session.add(search)

        raw_clip = RawClip(
            id=str(uuid4()),
            search_query_id=search.id,
            external_clip_id=payload.clip.clip_id,
            platform=payload.clip.platform,
            source_url=payload.clip.source_url,
            title=payload.clip.title,
            author_handle=payload.clip.author_handle,
            thumbnail_url=payload.clip.thumbnail_url,
            transcript_excerpt=payload.clip.transcript_excerpt,
            virality_score=payload.clip.virality_score,
            posted_at=payload.clip.posted_at,
            raw_payload={"source": "manual-save"},
        )
        session.add(raw_clip)
        session.flush()

        content_dna = ContentDNA(
            id=str(uuid4()),
            raw_clip_id=raw_clip.id,
            schema_version=payload.clip.content_dna.schema_version,
            clip_id=payload.clip.clip_id,
            source_url=payload.clip.source_url,
            platform=payload.clip.platform,
            virality_score=payload.clip.virality_score,
            posted_at=payload.clip.posted_at,
            niche=payload.clip.content_dna.niche,
            hook=payload.clip.content_dna.hook,
            format=payload.clip.content_dna.format,
            emotion=payload.clip.content_dna.emotion,
            structure=payload.clip.content_dna.structure,
            cta=payload.clip.content_dna.cta,
            replication_notes=payload.clip.content_dna.replication_notes,
        )
        session.add(content_dna)
        session.flush()
        self._sync_pattern_tags(session, content_dna, payload.clip.content_dna.pattern_tags)
        session.commit()
        session.refresh(content_dna)
        return content_dna

    def _sync_pattern_tags(self, session: Session, content_dna: ContentDNA, tags: list[str]) -> None:
        for value in tags:
            tag = session.scalar(select(PatternTag).where(PatternTag.value == value))
            if tag is None:
                tag = PatternTag(id=str(uuid4()), value=value)
                session.add(tag)
                session.flush()
            if tag not in content_dna.pattern_tags:
                content_dna.pattern_tags.append(tag)


@lru_cache(maxsize=1)
def get_library_service() -> LibraryService:
    return LibraryService()
