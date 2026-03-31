import Link from "next/link";
import { ContentDnaCard } from "@/components/content-dna-card";
import { SimilaritySearchPanel } from "@/components/similarity-search-panel";
import { defaultLibraryFilters, listLibrarySearchResults } from "@/lib/library-search";
import { listSimilarClips, searchSimilarity } from "@/lib/similarity";
import type { Platform } from "@/lib/types";

export const dynamic = "force-dynamic";

type SimilarPageProps = {
  params: { clipId: string };
  searchParams?: Record<string, string | string[] | undefined>;
};

export default async function SimilarClipsPage({ params, searchParams = {} }: SimilarPageProps) {
  const clipId = Number(params.clipId);
  const query = typeof searchParams.q === "string" ? searchParams.q : "";
  const platformParam = typeof searchParams.platform === "string" ? searchParams.platform : "all";
  const platform = platformParam === "tiktok" || platformParam === "youtube_shorts" ? platformParam : "all";

  const libraryItems = await listLibrarySearchResults(defaultLibraryFilters());
  const sourceItem = libraryItems.find((item) => item.content_dna.id === clipId);
  const similarity = query
    ? await searchSimilarity({ query, platform: platform as Platform | "all" })
    : await listSimilarClips(clipId, 5);

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Phase 3 similarity</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Use semantic retrieval to find the next pattern worth stealing.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
            Similarity search stays workspace-bounded but lets you move beyond exact hook or tag matches.
          </p>
          <Link href="/library/search" className="text-sm text-amber-300 underline-offset-4 hover:underline">
            Back to library search
          </Link>
        </div>
        <SimilaritySearchPanel clipId={clipId} initialQuery={query} initialPlatform={platform} />
      </section>

      {sourceItem ? (
        <section className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Source clip</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">{sourceItem.title}</h2>
          </div>
          <ContentDnaCard contentDna={sourceItem.content_dna} />
        </section>
      ) : (
        <section className="rounded-[2rem] border border-amber-400/20 bg-amber-400/10 p-6 text-sm text-amber-100">
          Source clip {clipId} was not found in the current library view, but semantic search is still available.
        </section>
      )}

      <section className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Matching clips</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">{similarity.items.length} result(s)</h2>
          </div>
          <p className="text-sm text-slate-400">
            Query: <span className="text-white">{similarity.query}</span> • provider <span className="text-white">{similarity.provider}</span>
          </p>
        </div>
        <div className="grid gap-5">
          {similarity.items.map((item) => (
            <article key={`${item.contentDnaId}-${item.matchedOn}`} className="space-y-4 rounded-[2rem] border border-white/10 bg-slate-950/55 p-6 shadow-glow">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="text-sm text-slate-300">
                  Match score <span className="text-white">{item.score.toFixed(2)}</span> • {item.matchedOn}
                </div>
                <Link
                  href={`/briefs?selectedClipIds=${item.contentDna.id ?? item.contentDnaId}`}
                  className="rounded-full border border-amber-400/30 bg-amber-400/10 px-4 py-2 text-sm text-amber-100 transition hover:border-amber-300/50"
                >
                  Use in brief
                </Link>
              </div>
              <ContentDnaCard contentDna={item.contentDna} />
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
