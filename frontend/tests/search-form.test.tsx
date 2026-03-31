import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SearchForm } from "@/components/search-form";
import { vi } from "vitest";

const push = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("SearchForm", () => {
  beforeEach(() => {
    push.mockClear();
  });

  it("submits the selected query and search filters", async () => {
    const user = userEvent.setup();
    render(<SearchForm initialQuery="meal prep" initialPlatforms={["tiktok"]} initialTimeframe="24h" initialMinVirality={80} />);

    await user.clear(screen.getByLabelText(/search query/i));
    await user.type(screen.getByLabelText(/search query/i), "meal prep hacks");
    await user.click(screen.getByRole("button", { name: /youtube shorts/i }));
    await user.click(screen.getByRole("button", { name: /run search/i }));

    expect(push).toHaveBeenCalledWith(
      expect.stringContaining("/search?q=meal+prep+hacks&platforms=tiktok%2Cyoutube_shorts&timeframe=24h&minVirality=80"),
    );
  });
});
