from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_search_service, resolve_identity
from app.schemas.library import LibraryItemCreate, LibraryItemRead
from app.services.identity import RequestIdentity
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/items", response_model=list[LibraryItemRead])
async def list_library_items(
    platform: str | None = None,
    hook: str | None = None,
    identity: RequestIdentity = Depends(resolve_identity),
    service: SearchService = Depends(get_search_service),
) -> list[LibraryItemRead]:
    return service.list_library_items(identity=identity, platform=platform, hook=hook)


@router.post("/items", response_model=LibraryItemRead)
async def save_library_item(
    payload: dict[str, object],
    identity: RequestIdentity = Depends(resolve_identity),
    service: SearchService = Depends(get_search_service),
) -> LibraryItemRead:
    if "content_dna_id" in payload:
        item = LibraryItemCreate.model_validate(payload)
    else:
        clip = payload.get("clip")
        content_dna_id = None
        note = payload.get("saved_note")
        if isinstance(clip, dict):
            content_dna = clip.get("content_dna")
            if isinstance(content_dna, dict):
                content_dna_id = content_dna.get("id")
        if not isinstance(content_dna_id, int):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="content_dna_id is required",
            )
        item = LibraryItemCreate(content_dna_id=content_dna_id, note=note if isinstance(note, str) else None)
    return service.save_library_item(identity=identity, item=item)
