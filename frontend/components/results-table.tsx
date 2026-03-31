import Link from "next/link";
import { ContentDnaCard } from "@/components/content-dna-card";
import { SaveToLibraryButton } from "@/components/save-to-library-button";
import type { PlatformFailure, SearchClip } from "@/lib/types";

interface ResultsTableProps {
  results: SearchClip[];
  searchId: string;
  partialFailures?: PlatformFailure[];
}

export function ResultsTable({ results, searchId, partialFailures = [] }: ResultsTableProps) {
  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Results</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">{results.length} ranked clips</h2>
            <p className="mt-2 text-sm text-slate-400">
              Search ID <span className="font-mono text-slate-200">{searchId}</span>
            </p>
          </div>
          <Link href="/library" className="text-sm text-amber-300 underline-offset-4 hover:underline">
            Review saved clips
          </Link>
        </div>
        {partialFailures.length > 0 ? (
          <div className="mt-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4 text-sm text-amber-100">
            {partialFailures.map((failure) => (
              <p key={failure.platform}>
                {failure.platform.replace("_", " ")} connector warning: {failure.message}
              </p>
            ))}
          </div>
        ) : null}
      </div>

      <div className="grid gap-5">
        {results.map((clip, index) => (
          <article
            key={clip.id}
            className="overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/55 shadow-glow"
          >
            <div className="grid gap-0 lg:grid-cols-[220px_1fr]">
              <div className="relative min-h-[220px] bg-slate-900">
                <img
                  src={clip.thumbnail_url}
                  alt={clip.title}
                  className="h-full w-full object-cover"
                />
                <div className="absolute left-4 top-4 rounded-full bg-black/60 px-3 py-1 text-xs uppercase tracking-[0.24em] text-white">
                  #{index + 1}
                </div>
              </div>
              <div className="space-y-5 p-5">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.24em] text-slate-500">
                      <span>{clip.platform.replace("_", " ")}</span>
                      <span>•</span>
                      <span>{clip.creator}</span>
                    </div>
                    <h3 className="mt-2 text-2xl font-semibold text-white">{clip.title}</h3>
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">{clip.summary}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-center">
                      <div className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Virality</div>
                      <div className="text-2xl font-semibold text-white">{clip.content_dna.virality_score}</div>
                    </div>
                    <SaveToLibraryButton clipId={clip.id} contentDnaId={clip.content_dna_id} saved={clip.saved} />
                  </div>
                </div>
                <ContentDnaCard contentDna={clip.content_dna} />
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
