from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.collections import router
from app.core.config import get_settings
from app.db.base import Base, create_engine_for_url
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.db.dependencies import get_session
from app.db.models.collection import Collection
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery


@pytest.fixture()
def client() -> TestClient:
    engine = create_engine_for_url("sqlite://")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    app = FastAPI()
    app.include_router(router, prefix="/api/library")

    def override_get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client


def _seed_item(session: Session, workspace_id: int) -> ContentDNA:
    search_query = SearchQuery(
        search_id="search-1",
        workspace_id=workspace_id,
        user_id=1,
        query_text="creator marketing",
        platforms=["tiktok"],
        timeframe="7d",
        min_virality_score=40.0,
        result_limit=10,
        status="completed",
    )
    raw_clip = RawClip(
        search_query=search_query,
        platform="tiktok",
        platform_clip_id="tiktok-1",
        source_url="https://example.com/1",
        title="Question hook",
        description="before after",
        author_name="Creator",
        author_handle="@creator",
        view_count=1000,
        like_count=100,
        comment_count=20,
        share_count=5,
        posted_at=datetime(2026, 3, 1, tzinfo=UTC),
        transcript="Comment for the template",
        frame_samples=["frame-1"],
        raw_payload={"source": "test"},
        normalized_score=91.0,
    )
    content_dna = ContentDNA(
        raw_clip=raw_clip,
        schema_version="1.0",
        clip_id="clip-1",
        source_url=raw_clip.source_url,
        platform="tiktok",
        virality_score=91.0,
        posted_at=raw_clip.posted_at,
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
    library_item = LibraryItem(
        workspace_id=workspace_id,
        content_dna=content_dna,
        note="save this",
    )
    session.add(library_item)
    session.commit()
    return content_dna


def test_create_list_and_attach_collection_item(client: TestClient) -> None:
    settings = get_settings()
    session_factory = client.app.dependency_overrides[get_session].__closure__[0].cell_contents  # type: ignore[attr-defined]
    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug=settings.default_workspace_slug, name="Personal")
        get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )
        content_dna = _seed_item(session, workspace.id)

    response = client.post("/api/library/collections", json={"name": "Hooks"})
    assert response.status_code == 200
    collection = response.json()
    assert collection["slug"] == "hooks"

    add_response = client.post(
        f"/api/library/collections/{collection['id']}/items",
        json={"content_dna_id": content_dna.id, "note": "watch later"},
    )
    assert add_response.status_code == 200
    assert add_response.json()["library_item"]["content_dna"]["clip_id"] == "clip-1"

    list_response = client.get("/api/library/collections")
    assert list_response.status_code == 200
    assert list_response.json()[0]["item_count"] == 1


def test_library_search_route_filters_saved_items(client: TestClient) -> None:
    settings = get_settings()
    session_factory = client.app.dependency_overrides[get_session].__closure__[0].cell_contents  # type: ignore[attr-defined]
    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug=settings.default_workspace_slug, name="Personal")
        get_or_create_user(
            session,
            workspace=workspace,
            external_id="user-1",
            email="user@example.com",
            display_name="User",
        )
        _seed_item(session, workspace.id)

    response = client.get("/api/library/search", params={"query": "template", "platform": "tiktok"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["content_dna"]["clip_id"] == "clip-1"
