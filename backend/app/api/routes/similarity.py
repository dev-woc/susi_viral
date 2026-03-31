from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import resolve_identity
from app.db.dependencies import get_session
from app.schemas.similarity import SimilaritySearchRequest, SimilaritySearchResponse
from app.services.identity import RequestIdentity
from app.services.similarity_search import SimilaritySearchService, get_similarity_search_service

router = APIRouter(prefix="/similarity")


@router.post("/search", response_model=SimilaritySearchResponse)
def search_similarity(
    payload: SimilaritySearchRequest,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: SimilaritySearchService = Depends(get_similarity_search_service),
) -> SimilaritySearchResponse:
    return service.search(session, payload, identity)


@router.get("/clips/{content_dna_id}", response_model=SimilaritySearchResponse)
def find_similar_clips(
    content_dna_id: int,
    limit: int = 5,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: SimilaritySearchService = Depends(get_similarity_search_service),
) -> SimilaritySearchResponse:
    return service.find_similar(session, content_dna_id, limit, identity)
