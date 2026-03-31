from fastapi import APIRouter

from app.api.routes import briefs, collections, health, library, reports, search, similarity, workspaces

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(library.router, prefix="/library", tags=["library"])
api_router.include_router(collections.router, prefix="/library", tags=["library"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(similarity.router, tags=["similarity"])
api_router.include_router(briefs.router, tags=["briefs"])
api_router.include_router(workspaces.router, tags=["workspaces"])
