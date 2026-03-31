import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ReportBuilderForm } from "@/components/report-builder-form";

const createReportDefinition = vi.hoisted(() => vi.fn());

vi.mock("@/lib/reports", async () => {
  const actual = await vi.importActual<typeof import("@/lib/reports")>("@/lib/reports");
  return {
    ...actual,
    createReportDefinition,
  };
});

describe("ReportBuilderForm", () => {
  afterEach(() => {
    createReportDefinition.mockReset();
  });

  it("saves a draft report with the selected cadence, platforms, and delivery channels", async () => {
    createReportDefinition.mockResolvedValue({
      id: "report_123",
      name: "Creator growth pulse",
      query: "creator growth",
      platforms: ["tiktok"],
      cadence: "daily",
      topN: 3,
      deliveryChannels: ["dashboard"],
      last_run_at: null,
      next_run_at: null,
      status: "scheduled",
      pattern_summary: "Mock report snapshot",
    });

    const user = userEvent.setup();
    render(<ReportBuilderForm />);

    await user.type(screen.getByLabelText(/report name/i), "Creator growth pulse");
    await user.type(screen.getByLabelText(/query or account list/i), "creator growth");
    await user.click(screen.getByRole("button", { name: /youtube shorts/i }));
    await user.click(screen.getByRole("button", { name: /email/i }));
    await user.selectOptions(screen.getByLabelText(/cadence/i), "daily");
    await user.clear(screen.getByLabelText(/top n/i));
    await user.type(screen.getByLabelText(/top n/i), "3");

    await user.click(screen.getByRole("button", { name: /save report/i }));

    expect(createReportDefinition).toHaveBeenCalledWith({
      name: "Creator growth pulse",
      query: "creator growth",
      platforms: ["tiktok"],
      cadence: "daily",
      topN: 3,
      deliveryChannels: ["dashboard"],
    });
    expect(await screen.findByText(/saved report draft/i)).toBeInTheDocument();
  });
});
