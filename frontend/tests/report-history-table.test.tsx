import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ReportHistoryTable } from "@/components/report-history-table";

describe("ReportHistoryTable", () => {
  it("renders the run history with statuses and delivery channels", () => {
    render(
      <ReportHistoryTable
        runs={[
          {
            id: "run_01",
            report_id: "report_01",
            started_at: "2026-03-29T09:00:00Z",
            finished_at: "2026-03-29T09:22:00Z",
            status: "complete",
            result_count: 10,
            delivery_targets: ["dashboard", "email"],
            notes: "Delivered on schedule.",
          },
          {
            id: "run_02",
            report_id: "report_02",
            started_at: "2026-03-30T07:15:00Z",
            finished_at: null,
            status: "partial",
            result_count: 5,
            delivery_targets: ["dashboard"],
            notes: "One connector failed but the snapshot was stored.",
          },
        ]}
      />,
    );

    expect(screen.getByText(/2 recent runs/i)).toBeInTheDocument();
    expect(screen.getByText("run_01")).toBeInTheDocument();
    expect(screen.getByText(/complete/i)).toBeInTheDocument();
    expect(screen.getByText(/partial/i)).toBeInTheDocument();
    expect(screen.getAllByText(/dashboard/i)).toHaveLength(2);
    expect(screen.getByText(/email/i)).toBeInTheDocument();
  });
});
