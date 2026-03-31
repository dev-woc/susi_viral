import { render, screen } from "@testing-library/react";
import { ContentDnaCard } from "@/components/content-dna-card";
import { demoSearchResponse } from "@/lib/mock-data";

describe("ContentDnaCard", () => {
  it("renders structured content DNA fields", () => {
    render(<ContentDnaCard contentDna={demoSearchResponse.results[0].content_dna} />);

    expect(screen.getByText(/contentdna/i)).toBeInTheDocument();
    expect(screen.getByText(/quick-cut tutorial/i)).toBeInTheDocument();
    expect(screen.getByText(/save this for sunday prep/i)).toBeInTheDocument();
  });
});
