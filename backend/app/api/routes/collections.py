from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_session
from app.schemas.collection import (
    CollectionCreateRequest,
    CollectionDetailResponse,
    CollectionItemCreateRequest,
    CollectionItemRead,
    CollectionRead,
    LibrarySearchRequest,
    LibrarySearchResponse,
)
from app.services.library_search import LibrarySearchService, get_library_search_service

router = APIRouter()


@router.get("/search", response_model=LibrarySearchResponse)
def search_library(
    query: str | None = None,
    platform: str | None = None,
    hook: str | None = None,
    format: str | None = None,
    pattern_tag: str | None = None,
    collection_id: int | None = None,
    limit: int = 25,
    session: Session = Depends(get_session),
    service: LibrarySearchService = Depends(get_library_search_service),
) -> LibrarySearchResponse:
    return service.search_request(
        session,
        LibrarySearchRequest(
            query=query,
            platform=platform,
            hook=hook,
            format=format,
            pattern_tag=pattern_tag,
            collection_id=collection_id,
            limit=limit,
        ),
    )


@router.post("/collections", response_model=CollectionRead)
def create_collection(
    payload: CollectionCreateRequest,
    session: Session = Depends(get_session),
    service: LibrarySearchService = Depends(get_library_search_service),
) -> CollectionRead:
    return service.create_collection(session, payload)


@router.get("/collections", response_model=list[CollectionRead])
def list_collections(
    session: Session = Depends(get_session),
    service: LibrarySearchService = Depends(get_library_search_service),
) -> list[CollectionRead]:
    return service.list_collections(session)


@router.get("/collections/{collection_id}", response_model=CollectionDetailResponse)
def get_collection(
    collection_id: int,
    session: Session = Depends(get_session),
    service: LibrarySearchService = Depends(get_library_search_service),
) -> CollectionDetailResponse:
    response = service.get_collection(session, collection_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return response


@router.post("/collections/{collection_id}/items", response_model=CollectionItemRead)
def add_collection_item(
    collection_id: int,
    payload: CollectionItemCreateRequest,
    session: Session = Depends(get_session),
    service: LibrarySearchService = Depends(get_library_search_service),
) -> CollectionItemRead:
    try:
        return service.add_item_to_collection(session, collection_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
