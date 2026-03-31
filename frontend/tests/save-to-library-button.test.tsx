import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SaveToLibraryButton } from "@/components/save-to-library-button";
import { vi } from "vitest";

const saveLibraryItem = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    id: "lib_clip_01",
  }),
);

vi.mock("@/lib/api", () => ({
  saveLibraryItem: (...args: unknown[]) => saveLibraryItem(...args),
}));

describe("SaveToLibraryButton", () => {
  it("shows a saved state after click", async () => {
    const user = userEvent.setup();
    render(<SaveToLibraryButton clipId="clip_01" />);

    await user.click(screen.getByRole("button", { name: /save to library/i }));

    expect(saveLibraryItem).toHaveBeenCalledWith({ clipId: "clip_01" });
    expect(await screen.findByRole("button", { name: /saved/i })).toBeDisabled();
  });
});
