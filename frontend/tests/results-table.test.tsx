import { render, screen } from "@testing-library/react";
import { ResultsTable } from "@/components/results-table";
import { demoSearchResponse } from "@/lib/mock-data";

describe("ResultsTable", () => {
  it("renders clips and partial failures", () => {
    render(
      <ResultsTable
        searchId={demoSearchResponse.search_id}
        results={demoSearchResponse.results}
        partialFailures={[
          { platform: "tiktok", message: "rate limited" },
        ]}
      />,
    );

    expect(screen.getByText(/3 ranked clips/i)).toBeInTheDocument();
    expect(screen.getByText(/tiktok connector warning/i)).toBeInTheDocument();
    expect(screen.getByText(/meal prep that finally stuck/i)).toBeInTheDocument();
  });
});
