from __future__ import annotations

import asyncio
from typing import Any

from app.db.runtime import session_factory
from app.services.reports.service import get_report_service
from app.tasks import celery_app


@celery_app.task(name="app.tasks.reports.run_scheduled_report")
def run_scheduled_report(report_id: int) -> dict[str, Any]:
    service = get_report_service()
    session = session_factory()
    try:
        run = asyncio.run(service.run_report(session, report_id, triggered_by="scheduled"))
        if run is None:
            return {"report_id": report_id, "status": "missing"}
        return {
            "report_id": report_id,
            "report_run_id": run.report_run_id,
            "status": run.status.value,
        }
    finally:
        session.close()
