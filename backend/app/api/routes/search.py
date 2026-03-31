from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_search_service, resolve_identity
from app.schemas.search import SearchDetailResponse, SearchRequest
from app.services.identity import RequestIdentity
from app.services.search_service import SearchService

router = APIRouter()


@router.post("", response_model=SearchDetailResponse)
async def create_search(
    payload: SearchRequest,
    identity: RequestIdentity = Depends(resolve_identity),
    service: SearchService = Depends(get_search_service),
) -> SearchDetailResponse:
    return await service.run_search(request=payload, identity=identity)


@router.get("/{search_id}", response_model=SearchDetailResponse)
async def get_search(
    search_id: str,
    service: SearchService = Depends(get_search_service),
) -> SearchDetailResponse:
    response = service.get_search(search_id=search_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search {search_id} was not found",
        )
    return response
