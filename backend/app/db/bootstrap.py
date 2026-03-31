from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models.user import User
from app.db.models.workspace import Workspace


def get_or_create_workspace(session: Session, slug: str, name: str) -> Workspace:
    workspace = session.scalar(select(Workspace).where(Workspace.slug == slug))
    if workspace is not None:
        if workspace.name != name and workspace.name == "Personal Workspace":
            workspace.name = name
        return workspace

    workspace = Workspace(slug=slug, name=name)
    session.add(workspace)
    session.flush()
    return workspace


def get_or_create_user(
    session: Session,
    workspace: Workspace,
    external_id: str,
    email: str,
    display_name: str,
) -> User:
    user = session.scalar(select(User).where(User.external_id == external_id))
    if user is not None:
        if user.workspace_id != workspace.id:
            user.workspace_id = workspace.id
        if email and user.email != email:
            user.email = email
        if display_name and user.display_name != display_name:
            user.display_name = display_name
        return user

    user = User(
        workspace_id=workspace.id,
        external_id=external_id,
        email=email,
        display_name=display_name,
    )
    session.add(user)
    session.flush()
    return user


def ensure_default_workspace(session: Session, settings: Settings) -> Workspace:
    return get_or_create_workspace(
        session,
        slug=settings.default_workspace_slug,
        name=settings.default_workspace_name,
    )


def ensure_default_user(session: Session, settings: Settings, workspace: Workspace) -> User:
    return get_or_create_user(
        session,
        workspace=workspace,
        external_id=settings.default_user_external_id,
        email=settings.default_user_email,
        display_name=settings.default_user_display_name,
    )
