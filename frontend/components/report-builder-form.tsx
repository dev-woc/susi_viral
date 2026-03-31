"use client";

import { useState, type FormEvent } from "react";
import { createReportDefinition, type DeliveryChannel, type ReportCadence } from "@/lib/reports";
import type { Platform } from "@/lib/types";

const platformOptions: { id: Platform; label: string }[] = [
  { id: "tiktok", label: "TikTok" },
  { id: "youtube_shorts", label: "YouTube Shorts" },
];

const cadenceOptions: { id: ReportCadence; label: string }[] = [
  { id: "daily", label: "Daily" },
  { id: "weekly", label: "Weekly" },
  { id: "custom", label: "Custom" },
];

const deliveryOptions: { id: DeliveryChannel; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "email", label: "Email" },
  { id: "pdf", label: "PDF" },
];

type ReportBuilderFormProps = {
  initialName?: string;
  initialQuery?: string;
  initialPlatforms?: Platform[];
  initialCadence?: ReportCadence;
  initialTopN?: number;
  initialDeliveryChannels?: DeliveryChannel[];
};

export function ReportBuilderForm({
  initialName = "",
  initialQuery = "",
  initialPlatforms = ["tiktok", "youtube_shorts"],
  initialCadence = "weekly",
  initialTopN = 10,
  initialDeliveryChannels = ["dashboard", "email"],
}: ReportBuilderFormProps) {
  const [name, setName] = useState(initialName);
  const [query, setQuery] = useState(initialQuery);
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>(initialPlatforms);
  const [cadence, setCadence] = useState<ReportCadence>(initialCadence);
  const [topN, setTopN] = useState(initialTopN);
  const [deliveryChannels, setDeliveryChannels] = useState<DeliveryChannel[]>(initialDeliveryChannels);
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  function togglePlatform(platform: Platform) {
    setSelectedPlatforms((current) =>
      current.includes(platform) ? current.filter((entry) => entry !== platform) : [...current, platform],
    );
  }

  function toggleDeliveryChannel(channel: DeliveryChannel) {
    setDeliveryChannels((current) =>
      current.includes(channel) ? current.filter((entry) => entry !== channel) : [...current, channel],
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const report = await createReportDefinition({
        name: name.trim() || "Untitled report",
        query: query.trim(),
        platforms: selectedPlatforms,
        cadence,
        topN,
        deliveryChannels,
      });

      setMessage(`Saved report draft "${report.name}" with ${report.platforms.length} platform(s).`);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <label htmlFor="report-name" className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">
          Report name
        </label>
        <input
          id="report-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Weekly niche monitor"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-base text-white outline-none transition placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </div>
      <div>
        <label htmlFor="report-query" className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">
          Query or account list
        </label>
        <input
          id="report-query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="fitness, creator growth, @competitor"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-base text-white outline-none transition placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Cadence</span>
          <select
            value={cadence}
            onChange={(event) => setCadence(event.target.value as ReportCadence)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          >
            {cadenceOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Top N</span>
          <input
            type="number"
            min={1}
            max={20}
            value={topN}
            onChange={(event) => setTopN(Number(event.target.value))}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
          <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Delivery</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {deliveryChannels.map((channel) => (
              <span key={channel} className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-100">
                {channel}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="space-y-3">
        <span className="block text-sm uppercase tracking-[0.24em] text-slate-400">Platforms</span>
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
      <div className="space-y-3">
        <span className="block text-sm uppercase tracking-[0.24em] text-slate-400">Delivery channels</span>
        <div className="flex flex-wrap gap-3">
          {deliveryOptions.map((channel) => {
            const selected = deliveryChannels.includes(channel.id);
            return (
              <button
                key={channel.id}
                type="button"
                onClick={() => toggleDeliveryChannel(channel.id)}
                className={`rounded-full border px-4 py-2 text-sm transition ${
                  selected
                    ? "border-amber-300/60 bg-amber-400/15 text-amber-100"
                    : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/10"
                }`}
              >
                {channel.label}
              </button>
            );
          })}
        </div>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-400">
          Drafts are saved through the API when available, and fall back to a local scaffold response when not.
        </p>
        <button
          type="submit"
          disabled={isSaving}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-orange-500/20 transition hover:translate-y-[-1px] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSaving ? "Saving..." : "Save report"}
        </button>
      </div>
      {message ? <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</p> : null}
    </form>
  );
}
