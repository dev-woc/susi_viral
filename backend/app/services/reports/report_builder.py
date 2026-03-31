from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from app.schemas.report import (
    ReportClipResult,
    ReportExecutionSnapshot,
    ReportStatus,
    ScheduledReportRead,
)


def build_pattern_summary(clips: list[ReportClipResult]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for clip in clips:
        for tag in clip.content_dna.pattern_tags:
            counter[tag] += 1
    return dict(sorted(counter.items()))


def build_pattern_deltas(
    current: dict[str, int],
    previous: dict[str, int] | None,
) -> dict[str, int]:
    previous_counts = previous or {}
    delta: dict[str, int] = {}
    for key in sorted(set(current) | set(previous_counts)):
        change = current.get(key, 0) - previous_counts.get(key, 0)
        if change != 0:
            delta[key] = change
    return delta


def build_report_snapshot(
    *,
    report: ScheduledReportRead,
    report_run_id: str,
    status: ReportStatus,
    total_fetched: int,
    total_ranked: int,
    partial_failures: list[Any],
    pattern_summary: dict[str, int],
    pattern_deltas: dict[str, int],
    top_clips: list[ReportClipResult],
    deliveries: list[dict[str, Any]],
    completed_at: datetime | None,
) -> ReportExecutionSnapshot:
    return ReportExecutionSnapshot(
        report_id=report.report_id,
        report_run_id=report_run_id,
        status=status,
        query_text=report.query_text,
        timeframe=report.timeframe,
        minimum_virality_score=report.minimum_virality_score,
        result_limit=report.result_limit,
        platforms=report.platforms,
        total_fetched=total_fetched,
        total_ranked=total_ranked,
        partial_failures=partial_failures,
        pattern_summary=pattern_summary,
        pattern_deltas=pattern_deltas,
        top_clips=top_clips,
        deliveries=deliveries,
        created_at=completed_at or report.created_at,
        completed_at=completed_at,
    )
