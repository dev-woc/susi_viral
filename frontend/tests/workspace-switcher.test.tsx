import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { WorkspaceSwitcher } from "@/components/workspace-switcher";

const refresh = vi.hoisted(() => vi.fn());
const switchWorkspace = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    refresh,
  }),
}));

vi.mock("@/lib/workspaces", async () => {
  const actual = await vi.importActual<typeof import("@/lib/workspaces")>("@/lib/workspaces");
  return {
    ...actual,
    switchWorkspace,
  };
});

describe("WorkspaceSwitcher", () => {
  afterEach(() => {
    refresh.mockReset();
    switchWorkspace.mockReset();
  });

  it("switches the active workspace and refreshes the page", async () => {
    switchWorkspace.mockResolvedValue({
      id: 2,
      slug: "agency",
      name: "Agency Workspace",
      createdAt: "2026-03-30T12:00:00Z",
      memberCount: 2,
      isActive: true,
    });

    const user = userEvent.setup();
    render(
      <WorkspaceSwitcher
        workspaces={[
          {
            id: 1,
            slug: "personal",
            name: "Personal Workspace",
            createdAt: "2026-03-30T12:00:00Z",
            memberCount: 1,
            isActive: true,
          },
        ]}
      />,
    );

    await user.clear(screen.getByLabelText(/workspace slug/i));
    await user.type(screen.getByLabelText(/workspace slug/i), "agency");
    await user.clear(screen.getByLabelText(/workspace name/i));
    await user.type(screen.getByLabelText(/workspace name/i), "Agency Workspace");
    await user.click(screen.getByRole("button", { name: /switch workspace/i }));

    expect(switchWorkspace).toHaveBeenCalledWith({
      workspaceSlug: "agency",
      workspaceName: "Agency Workspace",
    });
    expect(refresh).toHaveBeenCalled();
    expect(await screen.findByText(/active workspace is now/i)).toBeInTheDocument();
  });
});
