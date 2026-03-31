from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import resolve_identity
from app.db.dependencies import get_session
from app.schemas.workspace import (
    MonitorTargetCreateRequest,
    MonitorTargetListResponse,
    MonitorTargetRead,
    WorkspaceListResponse,
    WorkspaceSwitchRequest,
    WorkspaceSwitchResponse,
)
from app.services.identity import RequestIdentity
from app.services.monitoring.competitor_monitor import (
    CompetitorMonitorService,
    get_competitor_monitor_service,
)
from app.services.workspaces.service import WorkspaceService, get_workspace_service

router = APIRouter()


@router.get("/workspaces", response_model=WorkspaceListResponse)
def list_workspaces(
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceListResponse:
    return service.list_workspaces(session, identity)


@router.post("/workspaces/switch", response_model=WorkspaceSwitchResponse)
def switch_workspace(
    payload: WorkspaceSwitchRequest,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceSwitchResponse:
    return service.switch_workspace(session, payload, identity)


@router.post("/monitor-targets", response_model=MonitorTargetRead)
def create_monitor_target(
    payload: MonitorTargetCreateRequest,
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: CompetitorMonitorService = Depends(get_competitor_monitor_service),
) -> MonitorTargetRead:
    return service.create_target(session, payload, identity)


@router.get("/monitor-targets", response_model=MonitorTargetListResponse)
def list_monitor_targets(
    session: Session = Depends(get_session),
    identity: RequestIdentity = Depends(resolve_identity),
    service: CompetitorMonitorService = Depends(get_competitor_monitor_service),
) -> MonitorTargetListResponse:
    return service.list_targets(session, identity)
