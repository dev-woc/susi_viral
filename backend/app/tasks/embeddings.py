from __future__ import annotations

from app.db.base import session_scope
from app.db.runtime import session_factory
from app.services.embeddings.indexer import get_embedding_indexer
from app.tasks.celery_app import create_celery_app

celery_app = create_celery_app()


@celery_app.task(name="embeddings.index_workspace")
def index_workspace_embeddings(workspace_id: int) -> int:
    with session_scope(session_factory) as session:
        jobs = get_embedding_indexer().ensure_workspace_embeddings(session, workspace_id)
        return len(jobs)
