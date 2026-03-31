from fastapi import APIRouter

from app.api.routes import collections, health, library, reports, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(library.router, prefix="/library", tags=["library"])
api_router.include_router(collections.router, prefix="/library", tags=["library"])
api_router.include_router(reports.router, tags=["reports"])
