"use client";

import { useRouter } from "next/navigation";
import { startTransition, useState, type FormEvent } from "react";
import type { Platform, Timeframe } from "@/lib/types";

const platformOptions: { id: Platform; label: string }[] = [
  { id: "tiktok", label: "TikTok" },
  { id: "youtube_shorts", label: "YouTube Shorts" },
];

const timeframeOptions: { id: Timeframe; label: string }[] = [
  { id: "24h", label: "Last 24h" },
  { id: "7d", label: "Last 7d" },
  { id: "30d", label: "Last 30d" },
  { id: "all", label: "All time" },
];

interface SearchFormProps {
  initialQuery?: string;
  initialPlatforms?: Platform[];
  initialTimeframe?: Timeframe;
  initialMinVirality?: number;
}

export function SearchForm({
  initialQuery = "",
  initialPlatforms = ["tiktok", "youtube_shorts"],
  initialTimeframe = "7d",
  initialMinVirality = 70,
}: SearchFormProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>(initialPlatforms);
  const [timeframe, setTimeframe] = useState<Timeframe>(initialTimeframe);
  const [minVirality, setMinVirality] = useState(initialMinVirality);

  function togglePlatform(platform: Platform) {
    setSelectedPlatforms((current) =>
      current.includes(platform) ? current.filter((entry) => entry !== platform) : [...current, platform],
    );
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const params = new URLSearchParams();
    if (query.trim()) {
      params.set("q", query.trim());
    }
    params.set("platforms", selectedPlatforms.join(","));
    params.set("timeframe", timeframe);
    params.set("minVirality", String(minVirality));

    startTransition(() => {
      router.push(`/search?${params.toString()}`);
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <label htmlFor="query" className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">
          Search query
        </label>
        <input
          id="query"
          name="query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="niche, keyword, hashtag, account"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-base text-white outline-none transition placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Platforms</span>
          <div className="flex flex-wrap gap-3">
            {platformOptions.map((platform) => {
              const selected = selectedPlatforms.includes(platform.id);
              return (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => togglePlatform(platform.id)}
                  className={`rounded-full border px-4 py-2 text-sm transition ${
                    selected
                      ? "border-emerald-300/60 bg-emerald-400/15 text-emerald-100"
                      : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/10"
                  }`}
                >
                  {platform.label}
                </button>
              );
            })}
          </div>
        </div>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Timeframe</span>
          <select
            value={timeframe}
            onChange={(event) => setTimeframe(event.target.value as Timeframe)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          >
            {timeframeOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-[1fr_160px]">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">
            Minimum virality score
          </span>
          <input
            type="range"
            min={0}
            max={100}
            step={1}
            value={minVirality}
            onChange={(event) => setMinVirality(Number(event.target.value))}
            className="w-full accent-orange-500"
          />
        </label>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
          <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Threshold</div>
          <div className="mt-1 text-2xl font-semibold text-white">{minVirality}</div>
        </div>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-400">
          Phase 1 uses server-rendered results with a local fallback so the scaffold remains usable before backend wiring.
        </p>
        <button
          type="submit"
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-orange-500/20 transition hover:translate-y-[-1px]"
        >
          Run search
        </button>
      </div>
    </form>
  );
}
