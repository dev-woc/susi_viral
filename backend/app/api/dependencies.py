from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from app.core.config import Settings
from app.db.base import session_scope
from app.db.bootstrap import get_or_create_user, get_or_create_workspace
from app.services.identity import RequestIdentity
from app.services.search_service import SearchService


@dataclass(slots=True)
class IdentityMetadata:
    workspace_name: str
    user_email: str
    user_display_name: str


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service


def resolve_identity(request: Request) -> RequestIdentity:
    settings: Settings = request.app.state.settings
    session_factory = request.app.state.session_factory
    workspace_slug = request.headers.get("X-Workspace-Slug", settings.default_workspace_slug)
    workspace_name = request.headers.get("X-Workspace-Name", settings.default_workspace_name)
    user_external_id = request.headers.get("X-User-External-Id", settings.default_user_external_id)
    user_email = request.headers.get("X-User-Email", settings.default_user_email)
    user_display_name = request.headers.get("X-User-Display-Name", settings.default_user_display_name)

    with session_scope(session_factory) as session:
        workspace = get_or_create_workspace(session, slug=workspace_slug, name=workspace_name)
        user = get_or_create_user(
            session,
            workspace=workspace,
            external_id=user_external_id,
            email=user_email,
            display_name=user_display_name,
        )
        return RequestIdentity(
            workspace_id=workspace.id,
            user_id=user.id,
            workspace_slug=workspace.slug,
            user_external_id=user.external_id,
        )
