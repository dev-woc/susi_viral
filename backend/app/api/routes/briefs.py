from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import resolve_identity
from app.db.dependencies import get_session
from app.schemas.brief import ContentBriefCreateRequest, ContentBriefListResponse, ContentBriefRead
from app.services.briefs.content_brief_service import ContentBriefService, get_content_brief_service
from app.services.identity import RequestIdentity

router = APIRouter()


@router.post("/briefs", response_model=ContentBriefRead, status_code=status.HTTP_201_CREATED)
def create_brief(
    payload: ContentBriefCreateRequest,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: ContentBriefService = Depends(get_content_brief_service),
) -> ContentBriefRead:
    return service.create_brief(session, payload, identity)


@router.get("/briefs", response_model=ContentBriefListResponse)
def list_briefs(
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: ContentBriefService = Depends(get_content_brief_service),
) -> ContentBriefListResponse:
    return service.list_briefs(session, identity)


@router.get("/briefs/{brief_id}", response_model=ContentBriefRead)
def get_brief(
    brief_id: str,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: ContentBriefService = Depends(get_content_brief_service),
) -> ContentBriefRead:
    brief = service.get_brief(session, brief_id, identity)
    if brief is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content brief not found")
    return brief
