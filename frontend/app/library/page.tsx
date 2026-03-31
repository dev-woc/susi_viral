import { listLibraryItems } from "@/lib/api";

interface LibraryPageProps {
  searchParams?: Promise<Record<string, string | string[] | undefined>> | Record<string, string | string[] | undefined>;
}

export default async function LibraryPage({ searchParams = {} }: LibraryPageProps) {
  const resolvedSearchParams = await searchParams;
  const platform = typeof resolvedSearchParams.platform === "string" ? resolvedSearchParams.platform : "all";
  const hook = typeof resolvedSearchParams.hook === "string" ? resolvedSearchParams.hook : "all";
  const library = await listLibraryItems({
    platform: platform === "tiktok" || platform === "youtube_shorts" ? platform : "all",
    hook,
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <section className="space-y-6">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.28em] text-amber-300">Library</p>
          <h1 className="text-4xl font-semibold text-white sm:text-5xl">Saved clips for repeatable creative analysis.</h1>
          <p className="max-w-3xl text-lg leading-8 text-slate-300">
            This scaffold keeps the saved-item page server rendered and filterable, so the production backend can drop
            in without redesigning the UI.
          </p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
          <p className="text-sm text-slate-400">
            Showing {library.items.length} saved clips for platform <span className="text-white">{library.filters.platform}</span>
            {library.filters.hook !== "all" ? (
              <>
                {" "}
                and hook <span className="text-white">{library.filters.hook}</span>
              </>
            ) : null}
            .
          </p>
        </div>
        <div className="grid gap-5">
          {library.items.map((item) => (
            <article key={item.id} className="rounded-[2rem] border border-white/10 bg-slate-950/55 shadow-glow">
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
                  <h2 className="text-2xl font-semibold text-white">{item.title}</h2>
                  <p className="max-w-3xl text-sm leading-6 text-slate-300">{item.notes}</p>
                  <div className="flex flex-wrap gap-2">
                    {item.content_dna.pattern_tags.map((tag) => (
                      <span key={tag} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
