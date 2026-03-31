from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_session
from app.schemas.report import (
    ReportRunListResponse,
    ReportRunRead,
    ReportSearchRequest,
    ScheduledReportListResponse,
    ScheduledReportRead,
)
from app.services.reports.service import ReportService, get_report_service

router = APIRouter(prefix="/reports")
SessionDep = Annotated[Session, Depends(get_session)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


@router.post("", response_model=ScheduledReportRead, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportSearchRequest,
    session: SessionDep,
    service: ReportServiceDep,
) -> ScheduledReportRead:
    return service.create_report(session, payload)


@router.get("", response_model=ScheduledReportListResponse)
def list_reports(
    session: SessionDep,
    service: ReportServiceDep,
) -> ScheduledReportListResponse:
    return service.list_reports(session)


@router.get("/{report_id}", response_model=ScheduledReportRead)
def get_report(
    report_id: int,
    session: SessionDep,
    service: ReportServiceDep,
) -> ScheduledReportRead:
    report = service.get_report(session, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found",
        )
    return report


@router.patch("/{report_id}", response_model=ScheduledReportRead)
def update_report(
    report_id: int,
    payload: ReportSearchRequest,
    session: SessionDep,
    service: ReportServiceDep,
) -> ScheduledReportRead:
    report = service.update_report(session, report_id, payload)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found",
        )
    return report


@router.delete("/{report_id}", response_model=ScheduledReportRead)
def disable_report(
    report_id: int,
    session: SessionDep,
    service: ReportServiceDep,
) -> ScheduledReportRead:
    report = service.disable_report(session, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found",
        )
    return report


@router.post("/{report_id}/run", response_model=ReportRunRead)
async def run_report(
    report_id: int,
    session: SessionDep,
    service: ReportServiceDep,
) -> ReportRunRead:
    run = await service.run_report(session, report_id, triggered_by="manual")
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found",
        )
    return run


@router.get("/{report_id}/runs", response_model=ReportRunListResponse)
def list_runs(
    report_id: int,
    session: SessionDep,
    service: ReportServiceDep,
) -> ReportRunListResponse:
    return service.list_runs(session, report_id)
