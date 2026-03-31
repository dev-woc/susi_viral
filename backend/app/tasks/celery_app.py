from __future__ import annotations

from celery import Celery

from app.core.config import Settings, get_settings


def create_celery_app(settings: Settings | None = None) -> Celery:
    resolved = settings or get_settings()
    app = Celery("viral_content_agent", broker=resolved.redis_url, backend=resolved.redis_url)
    app.conf.update(task_always_eager=False, task_ignore_result=True)
    return app
