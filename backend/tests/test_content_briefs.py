from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.briefs import router as briefs_router
from app.api.routes.workspaces import router as workspaces_router
from app.core.config import Settings
from app.db.base import Base, create_engine_for_url
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.db.dependencies import get_session
from app.db.models.content_brief import ContentBrief
from app.db.models.content_dna import ContentDNA
from app.db.models.monitor_target import MonitorTarget
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.report_delivery import ReportDelivery  # noqa: F401
from app.db.models.scheduled_report import ReportRun, ScheduledReport  # noqa: F401
from app.db.models.search_query import SearchQuery
from app.db.models.workspace_membership import WorkspaceMembership
from app.services.briefs.content_brief_service import ContentBriefService
from app.services.identity import RequestIdentity
from app.schemas.brief import ContentBriefCreateRequest
from app.schemas.content_dna import PlatformName
from app.schemas.report import ReportFrequency, ReportPlatform
from app.schemas.search import Timeframe


def _build_session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = create_engine_for_url(f"sqlite:///{tmp_path / 'briefs.db'}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _seed_clip(session: Session, workspace_id: int, clip_id: int = 1) -> ContentDNA:
    search_query = SearchQuery(
        search_id=f"search-{clip_id}",
        workspace_id=workspace_id,
        user_id=1,
        query_text="creator planning",
        platforms=["tiktok"],
        timeframe="7d",
        min_virality_score=40.0,
        result_limit=10,
        status="completed",
    )
    raw_clip = RawClip(
        search_query=search_query,
        platform="tiktok",
        platform_clip_id=f"clip-{clip_id}",
        source_url=f"https://example.com/{clip_id}",
        title="Question hook",
        description="before after",
        author_name="Creator",
        author_handle="@creator",
        view_count=1000,
        like_count=100,
        comment_count=20,
        share_count=5,
        posted_at=None,
        transcript="Comment for the template",
        frame_samples=["frame-1"],
        raw_payload={"source": "test"},
        normalized_score=91.0,
    )
    content_dna = ContentDNA(
        raw_clip=raw_clip,
        schema_version="1.0",
        clip_id=f"clip-{clip_id}",
        source_url=raw_clip.source_url,
        platform=PlatformName.tiktok,
        virality_score=91.0,
        posted_at=None,
        niche="creator",
        hook="question hook",
        format="talking_head",
        emotion="curiosity",
        structure="hook -> body -> CTA",
        cta="comment below",
        replication_notes="use a strong opener",
        confidence=0.95,
        extracted_payload={"source": "test"},
    )
    content_dna.pattern_tags.append(PatternTag(name="question-hook", category="hook"))
    session.add(content_dna)
    session.commit()
    session.refresh(content_dna)
    return content_dna


def _build_identity(workspace_id: int, user_id: int = 1) -> RequestIdentity:
    return RequestIdentity(
        workspace_id=workspace_id,
        user_id=user_id,
        workspace_slug="personal",
        user_external_id="user-1",
    )


def test_brief_service_generates_persistent_brief(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'briefs.db'}")
    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )
        clip = _seed_clip(session, workspace.id)
        service = ContentBriefService()
        brief = service.create_brief(
            session,
            ContentBriefCreateRequest(
                title="Weekly hook brief",
                objective="Plan a hook-led creator video",
                audience="Solo creators",
                selected_content_dna_ids=[clip.id],
                tone="confident",
            ),
            _build_identity(workspace.id),
        )

        assert brief.summary
        assert brief.selected_content_dna_ids == [clip.id]
        assert brief.selected_clips[0].clip_id == clip.clip_id
        assert brief.recommended_shots
        assert brief.pattern_tags
        assert session.scalar(select(ContentBrief).where(ContentBrief.brief_id == brief.brief_id)) is not None


def test_brief_routes_support_create_list_and_get(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    app = FastAPI()
    app.include_router(briefs_router, prefix="/api")
    app.include_router(workspaces_router, prefix="/api")

    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    app.state.settings = Settings(database_url=f"sqlite:///{tmp_path / 'briefs.db'}")
    app.state.session_factory = session_factory

    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )
        clip = _seed_clip(session, workspace.id, clip_id=2)

    with TestClient(app) as client:
        response = client.post(
            "/api/briefs",
            json={
                "title": "Weekly hook brief",
                "objective": "Plan a hook-led creator video",
                "audience": "Solo creators",
                "selected_content_dna_ids": [clip.id],
                "tone": "confident",
            },
        )
        assert response.status_code == 201
        brief = response.json()
        assert brief["summary"]
        assert brief["selected_content_dna_ids"] == [clip.id]

        list_response = client.get("/api/briefs")
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) == 1

        get_response = client.get(f"/api/briefs/{brief['brief_id']}")
        assert get_response.status_code == 200
        assert get_response.json()["brief_id"] == brief["brief_id"]
