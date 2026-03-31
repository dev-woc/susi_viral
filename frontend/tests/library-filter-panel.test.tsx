import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LibraryFilterPanel } from "@/components/library-filter-panel";
import { buildLibrarySearchPath } from "@/lib/library-search";

const push = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
  }),
}));

describe("LibraryFilterPanel", () => {
  afterEach(() => {
    push.mockReset();
  });

  it("pushes a filtered library search path when submitted", async () => {
    const user = userEvent.setup();
    render(
      <LibraryFilterPanel
        initialFilters={{
          query: "",
          platform: "all",
          hook: "",
          format: "",
          tag: "",
        }}
      />,
    );

    await user.type(screen.getByLabelText(/keyword search/i), "creator growth");
    await user.selectOptions(screen.getByLabelText(/platform/i), "tiktok");
    await user.type(screen.getByLabelText(/hook contains/i), "question");
    await user.type(screen.getByLabelText(/format contains/i), "listicle");
    await user.type(screen.getByLabelText(/pattern tag/i), "before-after");
    await user.click(screen.getByRole("button", { name: /apply filters/i }));

    expect(push).toHaveBeenCalledWith(
      buildLibrarySearchPath({
        query: "creator growth",
        platform: "tiktok",
        hook: "question",
        format: "listicle",
        tag: "before-after",
      }),
    );
  });
});
