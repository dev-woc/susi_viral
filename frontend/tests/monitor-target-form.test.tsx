import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MonitorTargetForm } from "@/components/monitor-target-form";

const createMonitorTarget = vi.hoisted(() => vi.fn());

vi.mock("@/lib/workspaces", async () => {
  const actual = await vi.importActual<typeof import("@/lib/workspaces")>("@/lib/workspaces");
  return {
    ...actual,
    createMonitorTarget,
  };
});

describe("MonitorTargetForm", () => {
  afterEach(() => {
    createMonitorTarget.mockReset();
  });

  it("creates a monitor target with the selected inputs", async () => {
    createMonitorTarget.mockResolvedValue({
      id: "1",
      targetId: "target_01",
      workspaceId: 1,
      name: "Creator growth pulse",
      platform: "tiktok",
      accountHandle: "@competitor",
      queryText: "creator growth",
      cadence: "daily",
      enabled: true,
      notes: "Watch hook changes",
      lastRunAt: null,
      createdAt: "2026-03-30T12:00:00Z",
    });

    const user = userEvent.setup();
    render(<MonitorTargetForm />);

    await user.type(screen.getByLabelText(/target name/i), "Creator growth pulse");
    await user.type(screen.getByLabelText(/account handle/i), "@competitor");
    await user.type(screen.getByLabelText(/query text/i), "creator growth");
    await user.selectOptions(screen.getByLabelText(/cadence/i), "daily");
    await user.type(screen.getByLabelText(/notes/i), "Watch hook changes");
    await user.click(screen.getByRole("button", { name: /create target/i }));

    expect(createMonitorTarget).toHaveBeenCalledWith({
      name: "Creator growth pulse",
      platform: "tiktok",
      accountHandle: "@competitor",
      queryText: "creator growth",
      cadence: "daily",
      notes: "Watch hook changes",
    });
    expect(await screen.findByText(/saved monitor target/i)).toBeInTheDocument();
  });
});
