from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.similarity import router as similarity_router
from app.core.config import Settings
from app.db.base import Base, create_engine_for_url
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.db.dependencies import get_session
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery
from app.schemas.similarity import SimilaritySearchRequest
from app.services.identity import RequestIdentity
from app.services.similarity_search import SimilaritySearchService


def _build_session_factory(tmp_path: Path) -> sessionmaker[Session]:
    engine = create_engine_for_url(f"sqlite:///{tmp_path / 'similarity.db'}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _seed_item(session: Session, workspace_id: int, clip_id: int, hook: str, format_name: str) -> ContentDNA:
    search_query = SearchQuery(
        search_id=f"search-{clip_id}",
        workspace_id=workspace_id,
        user_id=1,
        query_text="creator growth",
        platforms=["tiktok"],
        timeframe="7d",
        min_virality_score=25.0,
        result_limit=10,
        status="completed",
    )
    raw_clip = RawClip(
        search_query=search_query,
        platform="tiktok",
        platform_clip_id=f"clip-{clip_id}",
        source_url=f"https://example.com/{clip_id}",
        title=f"Clip {clip_id}",
        description=f"{format_name} example",
        author_name="Creator",
        author_handle="@creator",
        view_count=1000 + clip_id,
        like_count=200,
        comment_count=20,
        share_count=10,
        posted_at=datetime(2026, 3, 1, tzinfo=UTC),
        transcript=hook,
        frame_samples=["frame-1"],
        raw_payload={"id": clip_id},
        normalized_score=70.0,
    )
    content_dna = ContentDNA(
        raw_clip=raw_clip,
        schema_version="1.0",
        clip_id=f"clip-{clip_id}",
        source_url=raw_clip.source_url,
        platform="tiktok",
        virality_score=80.0,
        posted_at=raw_clip.posted_at,
        niche="creator",
        hook=hook,
        format=format_name,
        emotion="curiosity",
        structure="hook -> proof -> CTA",
        cta="follow",
        replication_notes="Use the hook and pacing",
        confidence=0.8,
        extracted_payload={"source": "test"},
    )
    existing_tag = session.scalar(
        select(PatternTag).where(
            PatternTag.name == f"format:{format_name}",
            PatternTag.category == "format",
        )
    )
    content_dna.pattern_tags.append(
        existing_tag or PatternTag(name=f"format:{format_name}", category="format")
    )
    session.add(LibraryItem(workspace_id=workspace_id, content_dna=content_dna, note=f"saved {clip_id}"))
    session.commit()
    session.refresh(content_dna)
    return content_dna


def _identity(workspace_id: int) -> RequestIdentity:
    return RequestIdentity(workspace_id=workspace_id, user_id=1, workspace_slug="personal", user_external_id="user-1")


def test_similarity_service_returns_ranked_matches(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        get_or_create_user(session, workspace=workspace, external_id="user-1", email="user@example.com", display_name="User")
        clip_one = _seed_item(session, workspace.id, 1, "Question hook for creator growth", "talking_head")
        _seed_item(session, workspace.id, 2, "Tutorial format for growth systems", "tutorial")

        response = SimilaritySearchService().search(
            session,
            SimilaritySearchRequest(query="creator growth question hook", limit=2),
            _identity(workspace.id),
        )

        assert response.items
        assert response.items[0].content_dna_id == clip_one.id
        assert response.provider == "deterministic-local"


def test_similarity_routes_search_and_find_similar(tmp_path: Path) -> None:
    session_factory = _build_session_factory(tmp_path)
    app = FastAPI()
    app.include_router(similarity_router, prefix="/api")

    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    app.state.settings = Settings(database_url=f"sqlite:///{tmp_path / 'similarity.db'}")
    app.state.session_factory = session_factory

    with session_factory() as session:
        workspace = get_or_create_workspace(session, slug="personal", name="Personal")
        get_or_create_user(session, workspace=workspace, external_id="user-1", email="user@example.com", display_name="User")
        first = _seed_item(session, workspace.id, 1, "Question hook for creator growth", "talking_head")
        _seed_item(session, workspace.id, 2, "Question hook for creator planning", "talking_head")

    with TestClient(app) as client:
        response = client.post("/api/similarity/search", json={"query": "creator growth question hook", "limit": 2})
        assert response.status_code == 200
        assert response.json()["items"]

        similar_response = client.get(f"/api/similarity/clips/{first.id}")
        assert similar_response.status_code == 200
        assert similar_response.json()["items"]
