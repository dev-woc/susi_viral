import { SearchForm } from "@/components/search-form";
import { ResultsTable } from "@/components/results-table";
import { parsePlatformParam, parseTimeframeParam, searchClips } from "@/lib/api";

interface SearchPageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>> | Record<string, string | string[] | undefined>;
}

export default async function SearchPage({ searchParams = {} }: SearchPageProps) {
  const resolvedSearchParams = await searchParams;
  const query = typeof resolvedSearchParams.q === "string" ? resolvedSearchParams.q : "";
  const platforms = parsePlatformParam(resolvedSearchParams.platforms);
  const timeframe = parseTimeframeParam(resolvedSearchParams.timeframe);
  const minVirality = typeof resolvedSearchParams.minVirality === "string" ? Number(resolvedSearchParams.minVirality) : 70;

  const search = await searchClips({
    query,
    platforms,
    timeframe,
    minVirality: Number.isFinite(minVirality) ? minVirality : 70,
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <div className="grid gap-8">
        <section className="space-y-6">
          <div className="space-y-3">
            <p className="text-sm uppercase tracking-[0.28em] text-amber-300">Search workspace</p>
            <h1 className="text-4xl font-semibold text-white sm:text-5xl">Run an on-demand query and inspect the top clips.</h1>
            <p className="max-w-3xl text-lg leading-8 text-slate-300">
              The page is server rendered by default, but the form remains interactive so users can refine the query
              without leaving the app shell.
            </p>
          </div>
          <SearchForm
            initialQuery={query}
            initialPlatforms={platforms}
            initialTimeframe={timeframe}
            initialMinVirality={Number.isFinite(minVirality) ? minVirality : 70}
          />
        </section>

        <ResultsTable results={search.results} searchId={search.search_id} partialFailures={search.partial_failures} />
      </div>
    </div>
  );
}
