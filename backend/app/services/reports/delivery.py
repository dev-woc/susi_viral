from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.report import (
    ReportDeliveryChannel,
    ReportDeliveryStatus,
    ReportExecutionSnapshot,
    ScheduledReportRead,
)


class ReportDeliveryOutcome(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel: ReportDeliveryChannel
    destination: str | None = None
    status: ReportDeliveryStatus
    retryable: bool
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class DeliveryDispatcher:
    def dispatch(
        self,
        report: ScheduledReportRead,
        snapshot: ReportExecutionSnapshot,
    ) -> list[ReportDeliveryOutcome]:
        outcomes: list[ReportDeliveryOutcome] = []
        for channel in report.delivery_channels:
            if channel is ReportDeliveryChannel.dashboard:
                outcomes.append(
                    ReportDeliveryOutcome(
                        channel=channel,
                        destination="dashboard",
                        status=ReportDeliveryStatus.sent,
                        retryable=False,
                        message="Dashboard snapshot stored",
                        payload={
                            "report_id": report.report_id,
                            "report_run_id": snapshot.report_run_id,
                        },
                    )
                )
                continue

            if channel is ReportDeliveryChannel.email:
                if report.delivery_destination:
                    outcomes.append(
                        ReportDeliveryOutcome(
                            channel=channel,
                            destination=report.delivery_destination,
                            status=ReportDeliveryStatus.sent,
                            retryable=False,
                            message="Email delivery simulated",
                            payload={
                                "report_id": report.report_id,
                                "report_run_id": snapshot.report_run_id,
                            },
                        )
                    )
                else:
                    outcomes.append(
                        ReportDeliveryOutcome(
                            channel=channel,
                            destination=None,
                            status=ReportDeliveryStatus.failed,
                            retryable=False,
                            message="Email destination missing",
                            payload={
                                "report_id": report.report_id,
                                "report_run_id": snapshot.report_run_id,
                            },
                        )
                    )
                continue

            if channel is ReportDeliveryChannel.pdf:
                if snapshot.top_clips:
                    outcomes.append(
                        ReportDeliveryOutcome(
                            channel=channel,
                            destination=report.delivery_destination or "dashboard",
                            status=ReportDeliveryStatus.sent,
                            retryable=False,
                            message="PDF export simulated",
                            payload={
                                "report_id": report.report_id,
                                "report_run_id": snapshot.report_run_id,
                            },
                        )
                    )
                else:
                    outcomes.append(
                        ReportDeliveryOutcome(
                            channel=channel,
                            destination=report.delivery_destination or "dashboard",
                            status=ReportDeliveryStatus.failed,
                            retryable=True,
                            message="No clips available for PDF export",
                            payload={
                                "report_id": report.report_id,
                                "report_run_id": snapshot.report_run_id,
                            },
                        )
                    )
        return outcomes
