from __future__ import annotations

from celery import Celery

from app.core.config import get_settings
from app.db.base import create_engine_for_url, create_session_factory, initialize_database
from app.services.briefs.content_brief_service import ContentBriefService

settings = get_settings()
celery_app = Celery("viral_content_agent_briefs", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_always_eager=False, task_ignore_result=True)


@celery_app.task(name="generate_content_brief")
def generate_content_brief(payload: dict[str, object]) -> dict[str, object]:
    engine = create_engine_for_url(settings.database_url)
    initialize_database(engine)
    session_factory = create_session_factory(engine=engine)
    service = ContentBriefService()
    from app.schemas.brief import ContentBriefCreateRequest
    from app.services.identity import RequestIdentity

    identity = RequestIdentity(
        workspace_id=int(payload.get("workspace_id", 0) or 0),
        user_id=int(payload.get("user_id", 0) or 0),
        workspace_slug=str(payload.get("workspace_slug", settings.default_workspace_slug)),
        user_external_id=str(payload.get("user_external_id", settings.default_user_external_id)),
    )
    brief_payload = ContentBriefCreateRequest.model_validate(payload)
    with session_factory() as session:
        brief = service.create_brief(session, brief_payload, identity)
        return brief.model_dump(mode="json")
