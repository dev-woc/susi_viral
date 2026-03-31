from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.workspaces import router as workspaces_router
from app.api.routes.briefs import router as briefs_router
from app.core.config import Settings
from app.db.base import Base, create_engine_for_url
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.db.dependencies import get_session
from app.db.models.content_brief import ContentBrief  # noqa: F401
from app.db.models.monitor_target import MonitorTarget
from app.db.models.workspace_membership import WorkspaceMembership
from app.services.identity import RequestIdentity
from app.services.workspaces.service import WorkspaceService


def _build_session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = create_engine_for_url(f"sqlite:///{tmp_path / 'workspaces.db'}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _build_app(tmp_path: Path) -> tuple[FastAPI, sessionmaker[Session]]:
    session_factory = _build_session_factory(tmp_path)
    app = FastAPI()
    app.include_router(workspaces_router, prefix="/api")
    app.include_router(briefs_router, prefix="/api")

    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    app.state.settings = Settings(database_url=f"sqlite:///{tmp_path / 'workspaces.db'}")
    app.state.session_factory = session_factory
    return app, session_factory


def test_workspace_service_switches_and_lists_memberships(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        user = get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )
        service = WorkspaceService()
        workspaces = service.list_workspaces(session, RequestIdentity(
            workspace_id=workspace.id,
            user_id=user.id,
            workspace_slug=workspace.slug,
            user_external_id=user.external_id,
        ))

        assert workspaces.active_workspace_id == workspace.id
        assert workspaces.items

        switched = service.switch_workspace(
            session,
            __import__("app.schemas.workspace", fromlist=["WorkspaceSwitchRequest"]).WorkspaceSwitchRequest(
                workspace_slug="team-alpha",
                workspace_name="Team Alpha",
            ),
            RequestIdentity(
                workspace_id=workspace.id,
                user_id=user.id,
                workspace_slug=workspace.slug,
                user_external_id=user.external_id,
            ),
        )
        assert switched.workspace.slug == "team-alpha"
        assert session.query(WorkspaceMembership).count() >= 2


def test_workspace_routes_create_monitor_targets_and_list_workspaces(tmp_path: Path) -> None:
    app, session_factory = _build_app(tmp_path)

    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )

    with TestClient(app) as client:
        workspace_response = client.get("/api/workspaces")
        assert workspace_response.status_code == 200
        assert workspace_response.json()["items"][0]["slug"] == "personal"

        switch_response = client.post(
            "/api/workspaces/switch",
            json={"workspace_slug": "client-alpha", "workspace_name": "Client Alpha"},
        )
        assert switch_response.status_code == 200
        assert switch_response.json()["workspace"]["slug"] == "client-alpha"

        target_response = client.post(
            "/api/monitor-targets",
            json={
                "name": "Fitness competitor",
                "platform": "tiktok",
                "account_handle": "@fitcoach",
                "query_text": "fitness creator competitor",
                "cadence": "weekly",
                "enabled": True,
                "notes": "Track weekly cadence",
            },
        )
        assert target_response.status_code == 200
        assert target_response.json()["platform"] == "tiktok"

        target_list = client.get("/api/monitor-targets")
        assert target_list.status_code == 200
        assert len(target_list.json()["items"]) == 1
