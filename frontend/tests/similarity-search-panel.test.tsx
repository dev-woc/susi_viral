import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SimilaritySearchPanel } from "@/components/similarity-search-panel";
import { buildSimilarityPath } from "@/lib/similarity";

const push = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
  }),
}));

describe("SimilaritySearchPanel", () => {
  afterEach(() => {
    push.mockReset();
  });

  it("pushes a similarity route with the selected query and platform", async () => {
    const user = userEvent.setup();
    render(<SimilaritySearchPanel clipId={101} />);

    await user.type(screen.getByLabelText(/query/i), "creator growth");
    await user.selectOptions(screen.getByLabelText(/platform/i), "tiktok");
    await user.click(screen.getByRole("button", { name: /run similarity search/i }));

    expect(push).toHaveBeenCalledWith(
      buildSimilarityPath(101, {
        query: "creator growth",
        platform: "tiktok",
      }),
    );
  });
});
