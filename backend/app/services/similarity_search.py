from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.bootstrap import ensure_default_workspace
from app.db.models.collection_item import CollectionItem
from app.db.models.content_dna import ContentDNA
from app.db.models.embedding_job import EmbeddingJob
from app.db.models.library_item import LibraryItem
from app.schemas.content_dna import ContentDNARead, PatternTagData, PlatformName
from app.schemas.search import RawClipRead
from app.schemas.similarity import SimilarityResultRead, SimilaritySearchRequest, SimilaritySearchResponse
from app.services.embeddings.indexer import EmbeddingIndexer, get_embedding_indexer
from app.services.identity import RequestIdentity


class SimilaritySearchService:
    def __init__(self, indexer: EmbeddingIndexer | None = None) -> None:
        self.indexer = indexer or get_embedding_indexer()

    def search(
        self,
        session: Session,
        payload: SimilaritySearchRequest,
        identity: RequestIdentity | None = None,
    ) -> SimilaritySearchResponse:
        workspace_id = self._resolve_workspace_id(session, identity)
        jobs = self.indexer.ensure_workspace_embeddings(session, workspace_id)
        query_vector = self.indexer.encoder.encode_text(payload.query)
        scored = []
        for job in jobs:
            content_dna = self._load_content_dna(session, job.content_dna_id)
            if content_dna is None:
                continue
            if payload.platform and content_dna.platform != payload.platform.value:
                continue
            if payload.collection_id and not self._in_collection(session, payload.collection_id, content_dna.id):
                continue
            score = self.indexer.client.similarity(query_vector, list(job.vector_payload))
            scored.append((score, content_dna))

        scored.sort(key=lambda item: item[0], reverse=True)
        items = [
            SimilarityResultRead(
                content_dna_id=content_dna.id,
                score=round(score, 4),
                matched_on="semantic-query",
                content_dna=self._content_dna_read(content_dna),
            )
            for score, content_dna in scored[: payload.limit]
        ]
        return SimilaritySearchResponse(
            items=items,
            query=payload.query,
            provider="deterministic-local",
            generated_at=datetime.now(tz=UTC),
        )

    def find_similar(
        self,
        session: Session,
        content_dna_id: int,
        limit: int,
        identity: RequestIdentity | None = None,
    ) -> SimilaritySearchResponse:
        workspace_id = self._resolve_workspace_id(session, identity)
        base_job = self.indexer.ensure_embedding(session, workspace_id, content_dna_id)
        jobs = self.indexer.ensure_workspace_embeddings(session, workspace_id)
        scored = []
        for job in jobs:
            if job.content_dna_id == content_dna_id:
                continue
            content_dna = self._load_content_dna(session, job.content_dna_id)
            if content_dna is None:
                continue
            score = self.indexer.client.similarity(list(base_job.vector_payload), list(job.vector_payload))
            scored.append((score, content_dna))

        scored.sort(key=lambda item: item[0], reverse=True)
        base = self._load_content_dna(session, content_dna_id)
        query = base.hook if base and base.hook else f"content_dna:{content_dna_id}"
        return SimilaritySearchResponse(
            items=[
                SimilarityResultRead(
                    content_dna_id=content_dna.id,
                    score=round(score, 4),
                    matched_on="similar-clip",
                    content_dna=self._content_dna_read(content_dna),
                )
                for score, content_dna in scored[:limit]
            ],
            query=query,
            provider="deterministic-local",
            generated_at=datetime.now(tz=UTC),
        )

    def _resolve_workspace_id(self, session: Session, identity: RequestIdentity | None) -> int:
        if identity is not None:
            return identity.workspace_id
        workspace = ensure_default_workspace(session, __import__("app.core.config", fromlist=["get_settings"]).get_settings())
        return workspace.id

    def _load_content_dna(self, session: Session, content_dna_id: int) -> ContentDNA | None:
        return session.scalar(
            select(ContentDNA)
            .where(ContentDNA.id == content_dna_id)
            .options(selectinload(ContentDNA.pattern_tags), selectinload(ContentDNA.raw_clip))
        )

    def _in_collection(self, session: Session, collection_id: int, content_dna_id: int) -> bool:
        return session.scalar(
            select(CollectionItem.id).where(
                CollectionItem.collection_id == collection_id,
                CollectionItem.content_dna_id == content_dna_id,
            )
        ) is not None

    def _content_dna_read(self, content_dna: ContentDNA) -> ContentDNARead:
        return ContentDNARead(
            id=content_dna.id,
            raw_clip_id=content_dna.raw_clip_id,
            schema_version=content_dna.schema_version,
            clip_id=content_dna.clip_id,
            source_url=content_dna.source_url,
            platform=PlatformName(content_dna.platform),
            virality_score=content_dna.virality_score,
            posted_at=content_dna.posted_at,
            niche=content_dna.niche,
            hook=content_dna.hook,
            format=content_dna.format,
            emotion=content_dna.emotion,
            structure=content_dna.structure,
            cta=content_dna.cta,
            replication_notes=content_dna.replication_notes,
            pattern_tags=[PatternTagData(name=tag.name, category=tag.category) for tag in content_dna.pattern_tags],
            confidence=content_dna.confidence,
            created_at=content_dna.created_at,
        )


@lru_cache(maxsize=1)
def get_similarity_search_service() -> SimilaritySearchService:
    return SimilaritySearchService()
