from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.report import ReportFrequency, ReportPlatform


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    created_at: datetime
    member_count: int = 0
    is_active: bool = False


class WorkspaceListResponse(BaseModel):
    items: list[WorkspaceRead] = Field(default_factory=list)
    active_workspace_id: int | None = None


class WorkspaceSwitchRequest(BaseModel):
    workspace_slug: str = Field(min_length=1, max_length=80)
    workspace_name: str | None = Field(default=None, max_length=255)


class WorkspaceMembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    user_id: int
    role: str
    created_at: datetime


class WorkspaceSwitchResponse(BaseModel):
    workspace: WorkspaceRead
    membership: WorkspaceMembershipRead


class MonitorTargetCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    platform: ReportPlatform
    account_handle: str | None = Field(default=None, max_length=255)
    query_text: str = Field(min_length=1, max_length=500)
    cadence: ReportFrequency = ReportFrequency.weekly
    enabled: bool = True
    notes: str | None = Field(default=None, max_length=1000)


class MonitorTargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_id: str
    workspace_id: int
    user_id: int
    name: str
    platform: ReportPlatform
    account_handle: str | None = None
    query_text: str
    cadence: ReportFrequency
    enabled: bool
    notes: str | None = None
    last_run_at: datetime | None = None
    created_at: datetime


class MonitorTargetListResponse(BaseModel):
    items: list[MonitorTargetRead] = Field(default_factory=list)
