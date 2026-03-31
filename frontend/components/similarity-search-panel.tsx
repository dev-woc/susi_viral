"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { buildSimilarityPath } from "@/lib/similarity";
import type { Platform } from "@/lib/types";

const platformOptions: { id: Platform | "all"; label: string }[] = [
  { id: "all", label: "All platforms" },
  { id: "tiktok", label: "TikTok" },
  { id: "youtube_shorts", label: "YouTube Shorts" },
];

export function SimilaritySearchPanel({
  clipId,
  initialQuery = "",
  initialPlatform = "all",
}: {
  clipId: number;
  initialQuery?: string;
  initialPlatform?: Platform | "all";
}) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [platform, setPlatform] = useState<Platform | "all">(initialPlatform);
  const [searching, setSearching] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearching(true);
    router.push(
      buildSimilarityPath(clipId, {
        query,
        platform,
      }),
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Semantic search</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Refine similar clips by intent, not just fields.</h2>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Query</span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="creator growth question hooks"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Platform</span>
        <select
          value={platform}
          onChange={(event) => setPlatform(event.target.value as Platform | "all")}
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        >
          {platformOptions.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">If query is blank, the page falls back to clip-to-clip similarity.</p>
        <button
          type="submit"
          disabled={searching}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-70"
        >
          {searching ? "Searching..." : "Run similarity search"}
        </button>
      </div>
    </form>
  );
}
