from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base, create_engine_for_url
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.db.dependencies import get_session
from app.db.models.collection import Collection
from app.db.models.collection_item import CollectionItem
from app.db.models.content_dna import ContentDNA
from app.db.models.library_item import LibraryItem
from app.db.models.pattern_tag import PatternTag
from app.db.models.raw_clip import RawClip
from app.db.models.search_query import SearchQuery
from app.services.library_search import LibrarySearchFilters, LibrarySearchService


@pytest.fixture()
def session_factory() -> sessionmaker[Session]:
    engine = create_engine_for_url("sqlite://")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture()
def session(session_factory: sessionmaker[Session]) -> Session:
    with session_factory() as session:
        yield session


def _seed_library_item(
    session: Session,
    *,
    workspace_id: int,
    query_text: str,
    content_id: int,
    platform: str,
    title: str,
    description: str,
    transcript: str,
    hook: str,
    format_name: str,
    tags: list[tuple[str, str | None]],
) -> LibraryItem:
    search_query = SearchQuery(
        search_id=f"search-{content_id}",
        workspace_id=workspace_id,
        user_id=1,
        query_text=query_text,
        platforms=[platform],
        timeframe="7d",
        min_virality_score=40.0,
        result_limit=10,
        status="completed",
    )
    raw_clip = RawClip(
        search_query=search_query,
        platform=platform,
        platform_clip_id=f"{platform}-{content_id}",
        source_url=f"https://example.com/{content_id}",
        title=title,
        description=description,
        author_name="Creator",
        author_handle="@creator",
        view_count=1000 + content_id,
        like_count=200 + content_id,
        comment_count=50,
        share_count=10,
        posted_at=datetime(2026, 3, 1, tzinfo=UTC),
        transcript=transcript,
        frame_samples=["frame-1"],
        raw_payload={"id": content_id},
        normalized_score=80.0,
    )
    content_dna = ContentDNA(
        raw_clip=raw_clip,
        schema_version="1.0",
        clip_id=f"clip-{content_id}",
        source_url=raw_clip.source_url,
        platform=platform,
        virality_score=82.5,
        posted_at=raw_clip.posted_at,
        niche="fitness",
        hook=hook,
        format=format_name,
        emotion="curiosity",
        structure="Hook -> proof -> CTA",
        cta="Follow for more",
        replication_notes="Steal the pacing",
        confidence=0.9,
        extracted_payload={"source": "test"},
    )
    for name, category in tags:
        content_dna.pattern_tags.append(PatternTag(name=name, category=category))

    library_item = LibraryItem(
        workspace_id=workspace_id,
        content_dna=content_dna,
        note=f"note {content_id}",
    )
    session.add(library_item)
    session.commit()
    session.refresh(library_item)
    return library_item


def test_search_filters_by_text_platform_and_tag(session: Session) -> None:
    settings = get_settings()
    workspace = get_or_create_workspace(session, slug=settings.default_workspace_slug, name="Personal")
    user = get_or_create_user(
        session,
        workspace=workspace,
        external_id="user-1",
        email="user@example.com",
        display_name="User",
    )
    _seed_library_item(
        session,
        workspace_id=workspace.id,
        query_text="fitness hooks",
        content_id=1,
        platform="tiktok",
        title="Question hook workout",
        description="Strong before/after structure",
        transcript="Before and after challenge with a quick payoff",
        hook="question hook",
        format_name="talking_head",
        tags=[("before-after", "format"), ("question-hook", "hook")],
    )
    _seed_library_item(
        session,
        workspace_id=workspace.id,
        query_text="fitness hooks",
        content_id=2,
        platform="youtube_shorts",
        title="B-roll walkthrough",
        description="Slow demo",
        transcript="Here is the routine",
        hook="tutorial hook",
        format_name="voiceover_b_roll",
        tags=[("tutorial", "format")],
    )

    service = LibrarySearchService()
    response = service.search_library(
        session,
        LibrarySearchFilters(
            query="before after",
            platform="tiktok",
            hook="question",
            format="talking_head",
            pattern_tag="hook",
            limit=10,
        ),
    )

    assert response.total == 1
    assert response.items[0].content_dna.hook == "question hook"


def test_search_can_filter_by_collection(session: Session) -> None:
    settings = get_settings()
    workspace = get_or_create_workspace(session, slug=settings.default_workspace_slug, name="Personal")
    user = get_or_create_user(
        session,
        workspace=workspace,
        external_id="user-1",
        email="user@example.com",
        display_name="User",
    )
    first = _seed_library_item(
        session,
        workspace_id=workspace.id,
        query_text="fitness hooks",
        content_id=10,
        platform="tiktok",
        title="Question hook workout",
        description="Strong structure",
        transcript="Before and after challenge with a quick payoff",
        hook="question hook",
        format_name="talking_head",
        tags=[("before-after", "format")],
    )
    second = _seed_library_item(
        session,
        workspace_id=workspace.id,
        query_text="fitness hooks",
        content_id=11,
        platform="youtube_shorts",
        title="B-roll walkthrough",
        description="Slow demo",
        transcript="Here is the routine",
        hook="tutorial hook",
        format_name="voiceover_b_roll",
        tags=[("tutorial", "format")],
    )
    collection = Collection(workspace_id=workspace.id, name="Fitness", slug="fitness")
    session.add(collection)
    session.flush()
    session.add(CollectionItem(collection_id=collection.id, content_dna_id=first.content_dna.id))
    session.commit()

    response = LibrarySearchService().search_library(
        session,
        LibrarySearchFilters(collection_id=collection.id),
    )

    assert [item.content_dna.clip_id for item in response.items] == ["clip-10"]
    assert second.content_dna.clip_id not in [item.content_dna.clip_id for item in response.items]


def test_collection_crud_round_trip(session: Session) -> None:
    settings = get_settings()
    workspace = get_or_create_workspace(session, slug=settings.default_workspace_slug, name="Personal")
    get_or_create_user(
        session,
        workspace=workspace,
        external_id="user-1",
        email="user@example.com",
        display_name="User",
    )
    seeded = _seed_library_item(
        session,
        workspace_id=workspace.id,
        query_text="creator marketing",
        content_id=20,
        platform="tiktok",
        title="Strong opener",
        description="A simple opener",
        transcript="Comment for the template",
        hook="bold claim",
        format_name="voiceover_b_roll",
        tags=[("bold-claim", "hook")],
    )
    service = LibrarySearchService()
    collection = service.create_collection(
        session,
        __import__("app.schemas.collection", fromlist=["CollectionCreateRequest"]).CollectionCreateRequest(
            name="Creator Hooks"
        ),
    )
    assert collection.slug == "creator-hooks"

    item = service.add_item_to_collection(
        session,
        collection.id,
        __import__("app.schemas.collection", fromlist=["CollectionItemCreateRequest"]).CollectionItemCreateRequest(
            content_dna_id=seeded.content_dna.id,
            note="best clip"
        ),
    )
    assert item.library_item.content_dna.clip_id == "clip-20"

    detail = service.get_collection(session, collection.id)
    assert detail is not None
    assert detail.collection.item_count == 1
    assert detail.items[0].library_item.content_dna.clip_id == "clip-20"
