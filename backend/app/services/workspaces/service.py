from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.bootstrap import ensure_default_user, ensure_default_workspace, get_or_create_workspace
from app.db.models.monitor_target import MonitorTarget
from app.db.models.workspace import Workspace
from app.db.models.workspace_membership import WorkspaceMembership
from app.schemas.report import ReportFrequency, ReportPlatform
from app.schemas.workspace import (
    MonitorTargetCreateRequest,
    MonitorTargetListResponse,
    MonitorTargetRead,
    WorkspaceListResponse,
    WorkspaceMembershipRead,
    WorkspaceRead,
    WorkspaceSwitchRequest,
    WorkspaceSwitchResponse,
)
from app.services.identity import RequestIdentity


class WorkspaceService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def list_workspaces(self, session: Session, identity: RequestIdentity | None = None) -> WorkspaceListResponse:
        workspace, user = self._resolve_identity(session, identity)
        rows = list(
            session.scalars(
                select(Workspace)
                .join(
                    WorkspaceMembership,
                    WorkspaceMembership.workspace_id == Workspace.id,
                    isouter=True,
                )
                .where(
                    (Workspace.id == workspace.id)
                    | (WorkspaceMembership.user_id == user.id)
                    | (Workspace.slug == self.settings.default_workspace_slug)
                )
                .group_by(Workspace.id)
                .order_by(Workspace.created_at.asc())
            )
        )
        return WorkspaceListResponse(
            items=[
                WorkspaceRead(
                    id=row.id,
                    slug=row.slug,
                    name=row.name,
                    created_at=row.created_at,
                    member_count=self._member_count(session, row.id),
                    is_active=row.id == workspace.id,
                )
                for row in rows
            ],
            active_workspace_id=workspace.id,
        )

    def switch_workspace(
        self,
        session: Session,
        payload: WorkspaceSwitchRequest,
        identity: RequestIdentity | None = None,
    ) -> WorkspaceSwitchResponse:
        workspace, user = self._resolve_identity(session, identity)
        target = get_or_create_workspace(
            session,
            slug=payload.workspace_slug,
            name=payload.workspace_name or payload.workspace_slug.replace("-", " ").title(),
        )
        membership = self._ensure_membership(session, target.id, user.id)
        if workspace.id != target.id and user.workspace_id != target.id:
            user.workspace_id = target.id
            session.commit()
        return WorkspaceSwitchResponse(
            workspace=self._workspace_read(session, target, is_active=True),
            membership=WorkspaceMembershipRead.model_validate(membership),
        )

    def list_monitor_targets(
        self,
        session: Session,
        identity: RequestIdentity | None = None,
    ) -> MonitorTargetListResponse:
        workspace, _ = self._resolve_identity(session, identity)
        rows = list(
            session.scalars(
                select(MonitorTarget)
                .where(MonitorTarget.workspace_id == workspace.id)
                .order_by(MonitorTarget.created_at.desc())
            )
        )
        return MonitorTargetListResponse(items=[self._monitor_target_read(row) for row in rows])

    def create_monitor_target(
        self,
        session: Session,
        payload: MonitorTargetCreateRequest,
        identity: RequestIdentity | None = None,
    ) -> MonitorTargetRead:
        workspace, user = self._resolve_identity(session, identity)
        target = MonitorTarget(
            workspace_id=workspace.id,
            user_id=user.id,
            name=payload.name,
            platform=payload.platform.value,
            account_handle=payload.account_handle,
            query_text=payload.query_text,
            cadence=payload.cadence.value,
            enabled=payload.enabled,
            notes=payload.notes,
            created_at=datetime.now(tz=UTC),
        )
        session.add(target)
        session.commit()
        session.refresh(target)
        return self._monitor_target_read(target)

    def _resolve_identity(
        self, session: Session, identity: RequestIdentity | None
    ) -> tuple[Workspace, object]:
        if identity is None:
            workspace = ensure_default_workspace(session, self.settings)
            user = ensure_default_user(session, self.settings, workspace)
            self._ensure_membership(session, workspace.id, user.id)
            return workspace, user

        workspace = session.get(Workspace, identity.workspace_id)
        if workspace is None:
            workspace = ensure_default_workspace(session, self.settings)
        user = ensure_default_user(session, self.settings, workspace)
        if user.id != identity.user_id:
            user = session.get(type(user), identity.user_id) or user
        self._ensure_membership(session, workspace.id, user.id)
        return workspace, user

    def _ensure_membership(self, session: Session, workspace_id: int, user_id: int) -> WorkspaceMembership:
        membership = session.scalar(
            select(WorkspaceMembership).where(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
        )
        if membership is None:
            membership = WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role="owner")
            session.add(membership)
            try:
                session.commit()
                session.refresh(membership)
            except IntegrityError:
                session.rollback()
                membership = session.scalar(
                    select(WorkspaceMembership).where(
                        WorkspaceMembership.workspace_id == workspace_id,
                        WorkspaceMembership.user_id == user_id,
                    )
                )
                if membership is None:
                    raise
        return membership

    def _member_count(self, session: Session, workspace_id: int) -> int:
        return session.scalar(
            select(func.count(WorkspaceMembership.id)).where(
                WorkspaceMembership.workspace_id == workspace_id
            )
        ) or 0

    def _workspace_read(self, session: Session, workspace: Workspace, is_active: bool) -> WorkspaceRead:
        return WorkspaceRead(
            id=workspace.id,
            slug=workspace.slug,
            name=workspace.name,
            created_at=workspace.created_at,
            member_count=self._member_count(session, workspace.id),
            is_active=is_active,
        )

    def _monitor_target_read(self, target: MonitorTarget) -> MonitorTargetRead:
        return MonitorTargetRead(
            id=target.id,
            target_id=target.target_id,
            workspace_id=target.workspace_id,
            user_id=target.user_id,
            name=target.name,
            platform=ReportPlatform(target.platform),
            account_handle=target.account_handle,
            query_text=target.query_text,
            cadence=ReportFrequency(target.cadence),
            enabled=target.enabled,
            notes=target.notes,
            last_run_at=target.last_run_at,
            created_at=target.created_at,
        )


@lru_cache(maxsize=1)
def get_workspace_service() -> WorkspaceService:
    return WorkspaceService()
