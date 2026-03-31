from __future__ import annotations

from functools import lru_cache
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.content_dna import ContentDNA
from app.db.models.embedding_job import EmbeddingJob
from app.db.models.library_item import LibraryItem
from app.services.embeddings.encoder import EmbeddingEncoder
from app.services.embeddings.qdrant_client import QdrantClient


class EmbeddingIndexer:
    def __init__(self) -> None:
        self.encoder = EmbeddingEncoder()
        self.client = QdrantClient()

    def ensure_embedding(self, session: Session, workspace_id: int, content_dna_id: int) -> EmbeddingJob:
        job = session.scalar(
            select(EmbeddingJob).where(
                EmbeddingJob.workspace_id == workspace_id,
                EmbeddingJob.content_dna_id == content_dna_id,
            )
        )
        if job is not None:
            return job

        content_dna = session.scalar(
            select(ContentDNA)
            .where(ContentDNA.id == content_dna_id)
            .options(selectinload(ContentDNA.pattern_tags))
        )
        if content_dna is None:
            raise LookupError(f"content_dna_id {content_dna_id} not found")

        vector = self.encoder.encode_content_dna(content_dna)
        job = EmbeddingJob(
            job_id=uuid4().hex,
            workspace_id=workspace_id,
            content_dna_id=content_dna_id,
            status="completed",
            provider="deterministic-local",
            vector_size=len(vector),
            vector_payload=vector,
            job_metadata={"text": self.encoder.build_text(content_dna)},
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job

    def ensure_workspace_embeddings(self, session: Session, workspace_id: int) -> list[EmbeddingJob]:
        content_ids = list(
            session.scalars(
                select(LibraryItem.content_dna_id).where(LibraryItem.workspace_id == workspace_id)
            )
        )
        return [self.ensure_embedding(session, workspace_id, content_id) for content_id in content_ids]


@lru_cache(maxsize=1)
def get_embedding_indexer() -> EmbeddingIndexer:
    return EmbeddingIndexer()
