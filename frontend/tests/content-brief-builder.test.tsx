import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ContentBriefBuilder } from "@/components/content-brief-builder";

const createBrief = vi.hoisted(() => vi.fn());

vi.mock("@/lib/briefs", async () => {
  const actual = await vi.importActual<typeof import("@/lib/briefs")>("@/lib/briefs");
  return {
    ...actual,
    createBrief,
  };
});

describe("ContentBriefBuilder", () => {
  afterEach(() => {
    createBrief.mockReset();
  });

  it("creates a brief with selected content dna ids", async () => {
    createBrief.mockResolvedValue({
      id: "brief_01",
      briefId: "brief_01",
      title: "Creator growth sprint",
      objective: "Increase saves",
      audience: "Solo creators",
      tone: "direct",
      summary: "Mock summary",
      recommendedShots: [],
      selectedContentDnaIds: [101, 102],
      patternTags: [],
      createdAt: "2026-03-30T12:00:00Z",
      updatedAt: "2026-03-30T12:00:00Z",
      selectedClips: [],
    });

    const user = userEvent.setup();
    render(<ContentBriefBuilder initialSelectedContentDnaIds={[101]} />);

    await user.type(screen.getByLabelText(/title/i), "Creator growth sprint");
    await user.type(screen.getByLabelText(/objective/i), "Increase saves");
    await user.type(screen.getByLabelText(/audience/i), "Solo creators");
    await user.type(screen.getByLabelText(/tone/i), "direct");
    await user.clear(screen.getByLabelText(/selected clip ids/i));
    await user.type(screen.getByLabelText(/selected clip ids/i), "101, 102");
    await user.click(screen.getByRole("button", { name: /create brief/i }));

    expect(createBrief).toHaveBeenCalledWith({
      title: "Creator growth sprint",
      objective: "Increase saves",
      audience: "Solo creators",
      tone: "direct",
      notes: undefined,
      selectedContentDnaIds: [101, 102],
    });
    expect(await screen.findByText(/saved brief/i)).toBeInTheDocument();
  });
});
