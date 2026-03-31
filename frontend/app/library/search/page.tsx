import { LibraryFilterPanel } from "@/components/library-filter-panel";
import {
  filterLibraryItems,
  isLibraryBackendConfigured,
  listLibrarySearchResults,
  parseLibrarySearchParams,
} from "@/lib/library-search";
import { ContentDnaCard } from "@/components/content-dna-card";

export const dynamic = "force-dynamic";

type LibrarySearchPageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

export default async function LibrarySearchPage({ searchParams = {} }: LibrarySearchPageProps) {
  const filters = parseLibrarySearchParams(searchParams);
  const items = await listLibrarySearchResults(filters);
  const visibleItems = filterLibraryItems(items, filters);
  const backendConfigured = isLibraryBackendConfigured();

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Library search</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Find saved clips by the element that actually matters.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
            Phase 2 uses field filters and full-text style matching to retrieve clips by hook, format, tag, or note
            instead of forcing you to browse the entire saved library.
          </p>
          <p className="text-sm text-slate-400">
            Backend available: <span className="text-white">{backendConfigured ? "yes" : "no"}</span>
          </p>
        </div>
        <LibraryFilterPanel initialFilters={filters} />
      </section>

      <section className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Matching clips</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">{visibleItems.length} saved clips</h2>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-slate-400">
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
              platform {filters.platform}
            </span>
            {filters.hook ? <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">hook {filters.hook}</span> : null}
            {filters.format ? <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">format {filters.format}</span> : null}
            {filters.tag ? <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">tag {filters.tag}</span> : null}
          </div>
        </div>
        <div className="grid gap-5">
          {visibleItems.map((item) => (
            <article key={item.id} className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/5 shadow-glow">
              <div className="grid gap-0 lg:grid-cols-[220px_1fr]">
                <img src={item.thumbnail_url} alt={item.title} className="h-full min-h-[220px] w-full object-cover" />
                <div className="space-y-4 p-5">
                  <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.24em] text-slate-500">
                    <span>{item.platform.replace("_", " ")}</span>
                    <span>•</span>
                    <span>{item.creator}</span>
                    <span>•</span>
                    <span>{new Date(item.saved_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="text-2xl font-semibold text-white">{item.title}</h3>
                  <p className="max-w-3xl text-sm leading-6 text-slate-300">{item.notes}</p>
                  <ContentDnaCard contentDna={item.content_dna} />
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
