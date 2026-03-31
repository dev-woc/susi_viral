from __future__ import annotations

import importlib.util
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.db.base import Base, create_engine_for_url
from app.db.dependencies import get_session
from app.db.models.report_delivery import ReportDelivery  # noqa: F401
from app.db.models.scheduled_report import ReportRun, ScheduledReport  # noqa: F401
from app.db.models.user import User  # noqa: F401
from app.db.models.workspace import Workspace  # noqa: F401
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

_REPORTS_ROUTE_PATH = Path(__file__).resolve().parents[1] / "app" / "api" / "routes" / "reports.py"
_REPORTS_ROUTE_SPEC = importlib.util.spec_from_file_location(
    "backend_app_api_routes_reports",
    _REPORTS_ROUTE_PATH,
)
assert _REPORTS_ROUTE_SPEC is not None and _REPORTS_ROUTE_SPEC.loader is not None
_REPORTS_ROUTE_MODULE = importlib.util.module_from_spec(_REPORTS_ROUTE_SPEC)
_REPORTS_ROUTE_SPEC.loader.exec_module(_REPORTS_ROUTE_MODULE)
reports_router = _REPORTS_ROUTE_MODULE.router


@contextmanager
def _build_test_client(tmp_path: Path) -> Iterator[TestClient]:
    engine = create_engine_for_url(f"sqlite:///{tmp_path / 'reports.db'}")
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(reports_router, prefix="/api")

    def override_get_session() -> Iterator[Session]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_create_run_and_read_report_history(tmp_path: Path) -> None:
    with _build_test_client(tmp_path) as client:
        payload = {
            "name": "Weekly hooks report",
            "query_text": "growth marketing",
            "platforms": [
                "tiktok",
                "youtube_shorts",
                "instagram_reels",
                "twitter_x",
                "reddit",
            ],
            "timeframe": "7d",
            "minimum_virality_score": 20,
            "result_limit": 5,
            "format_filters": ["before_after"],
            "cadence": "weekly",
            "delivery_channels": ["dashboard", "email"],
            "delivery_destination": "team@example.com",
            "notes": "Demo report",
            "enabled": True,
        }

        create_response = client.post("/api/reports", json=payload)
        assert create_response.status_code == 201
        report = create_response.json()
        assert report["enabled"] is True
        assert report["latest_run"] is None

        list_response = client.get("/api/reports")
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) == 1

        run_response = client.post(f"/api/reports/{report['id']}/run")
        assert run_response.status_code == 200
        run = run_response.json()
        assert run["report_run_id"]
        assert run["status"] in {"complete", "partial"}
        assert len(run["deliveries"]) == 2

        report_response = client.get(f"/api/reports/{report['id']}")
        assert report_response.status_code == 200
        report_detail = report_response.json()
        assert report_detail["latest_run"]["report_run_id"] == run["report_run_id"]

        runs_response = client.get(f"/api/reports/{report['id']}/runs")
        assert runs_response.status_code == 200
        assert len(runs_response.json()["items"]) == 1


def test_disable_report_marks_report_inactive(tmp_path: Path) -> None:
    with _build_test_client(tmp_path) as client:
        create_response = client.post(
            "/api/reports",
            json={
                "name": "Daily scan",
                "query_text": "creator systems",
                "platforms": ["tiktok"],
                "timeframe": "24h",
                "minimum_virality_score": 10,
                "result_limit": 3,
                "cadence": "daily",
                "delivery_channels": ["dashboard"],
                "enabled": True,
            },
        )
        report_id = create_response.json()["id"]

        disable_response = client.delete(f"/api/reports/{report_id}")
        assert disable_response.status_code == 200
        assert disable_response.json()["enabled"] is False
