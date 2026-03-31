from __future__ import annotations

from functools import lru_cache

from sqlalchemy.orm import Session

from app.schemas.workspace import MonitorTargetCreateRequest, MonitorTargetListResponse, MonitorTargetRead
from app.services.identity import RequestIdentity
from app.services.workspaces.service import WorkspaceService, get_workspace_service


class CompetitorMonitorService:
    def __init__(self, workspace_service: WorkspaceService | None = None) -> None:
        self.workspace_service = workspace_service or get_workspace_service()

    def create_target(
        self,
        session: Session,
        payload: MonitorTargetCreateRequest,
        identity: RequestIdentity | None = None,
    ) -> MonitorTargetRead:
        return self.workspace_service.create_monitor_target(session, payload, identity)

    def list_targets(
        self,
        session: Session,
        identity: RequestIdentity | None = None,
    ) -> MonitorTargetListResponse:
        return self.workspace_service.list_monitor_targets(session, identity)


@lru_cache(maxsize=1)
def get_competitor_monitor_service() -> CompetitorMonitorService:
    return CompetitorMonitorService()
