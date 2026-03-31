"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { buildLibrarySearchPath, type LibraryFilterState } from "@/lib/library-search";
import type { Platform } from "@/lib/types";

const platformOptions: { id: Platform | "all"; label: string }[] = [
  { id: "all", label: "All platforms" },
  { id: "tiktok", label: "TikTok" },
  { id: "youtube_shorts", label: "YouTube Shorts" },
];

type LibraryFilterPanelProps = {
  initialFilters: LibraryFilterState;
};

export function LibraryFilterPanel({ initialFilters }: LibraryFilterPanelProps) {
  const router = useRouter();
  const [filters, setFilters] = useState(initialFilters);
  const [navigating, setNavigating] = useState(false);

  function updateField<K extends keyof LibraryFilterState>(key: K, value: LibraryFilterState[K]) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNavigating(true);
    router.push(buildLibrarySearchPath(filters));
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Library filters</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Search saved clips by element field</h2>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Keyword search</span>
        <input
          value={filters.query}
          onChange={(event) => updateField("query", event.target.value)}
          placeholder="hook, format, pattern tag, note"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Platform</span>
          <select
            value={filters.platform}
            onChange={(event) => updateField("platform", event.target.value as LibraryFilterState["platform"])}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          >
            {platformOptions.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Hook contains</span>
          <input
            value={filters.hook}
            onChange={(event) => updateField("hook", event.target.value)}
            placeholder="question, bold claim, before-after"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Format contains</span>
          <input
            value={filters.format}
            onChange={(event) => updateField("format", event.target.value)}
            placeholder="talking head, voiceover, listicle"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Pattern tag</span>
          <input
            value={filters.tag}
            onChange={(event) => updateField("tag", event.target.value)}
            placeholder="before-after, comment-cta"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
      </div>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">
          Server-rendered defaults stay in place until the backend search endpoint is connected.
        </p>
        <button
          type="submit"
          disabled={navigating}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-70"
        >
          {navigating ? "Filtering..." : "Apply filters"}
        </button>
      </div>
    </form>
  );
}
