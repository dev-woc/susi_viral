import Link from "next/link";
import { SearchForm } from "@/components/search-form";
import { demoSearchResponse } from "@/lib/mock-data";

export default function HomePage() {
  const featured = demoSearchResponse.results.slice(0, 2);

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
      <section className="grid gap-8 lg:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-8">
          <div className="inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.32em] text-slate-300">
            Phase 1 MVP scaffold
          </div>
          <div className="space-y-5">
            <p className="text-sm uppercase tracking-[0.28em] text-amber-300">Viral Content Agent</p>
            <h1 className="max-w-3xl text-5xl font-semibold leading-[0.95] text-white sm:text-6xl">
              Search the clips that already know how to win attention.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              This frontend scaffold is built for server-rendered reads, rapid search iteration, and structured
              `ContentDNA` review across TikTok and YouTube Shorts.
            </p>
          </div>
          <SearchForm />
          <div className="flex flex-wrap gap-3 text-sm text-slate-400">
            <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2">TikTok connector ready</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2">YouTube Shorts ready</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2">Clerk provider wired</span>
          </div>
        </div>
        <aside className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">What ships in Phase 1</p>
          <div className="mt-6 space-y-4">
            {[
              "On-demand search with platform selection and virality thresholds",
              "Structured `ContentDNA` rendering for each clip",
              "Manual save-to-library workflow with typed API access",
              "Server-rendered routes for home, search, and library",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-sm text-slate-200">
                {item}
              </div>
            ))}
          </div>
          <div className="mt-6 space-y-4">
            {featured.map((clip) => (
              <div key={clip.id} className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/40">
                <img src={clip.thumbnail_url} alt={clip.title} className="h-40 w-full object-cover" />
                <div className="space-y-2 p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{clip.platform.replace("_", " ")}</p>
                  <h2 className="text-lg font-semibold text-white">{clip.title}</h2>
                  <p className="text-sm text-slate-300">{clip.content_dna.hook}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6">
            <Link
              href="/search"
              className="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:translate-y-[-1px]"
            >
              Open search workspace
            </Link>
          </div>
        </aside>
      </section>
    </div>
  );
}
