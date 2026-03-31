"use client";

import { useState, type FormEvent } from "react";
import { createMonitorTarget, type MonitorCadence, type MonitorPlatform } from "@/lib/workspaces";

const platformOptions: { id: MonitorPlatform; label: string }[] = [
  { id: "tiktok", label: "TikTok" },
  { id: "youtube_shorts", label: "YouTube Shorts" },
  { id: "instagram_reels", label: "Instagram Reels" },
  { id: "twitter_x", label: "X" },
  { id: "reddit", label: "Reddit" },
];

const cadenceOptions: { id: MonitorCadence; label: string }[] = [
  { id: "daily", label: "Daily" },
  { id: "weekly", label: "Weekly" },
  { id: "custom", label: "Custom" },
];

export function MonitorTargetForm() {
  const [name, setName] = useState("");
  const [platform, setPlatform] = useState<MonitorPlatform>("tiktok");
  const [accountHandle, setAccountHandle] = useState("");
  const [queryText, setQueryText] = useState("");
  const [cadence, setCadence] = useState<MonitorCadence>("weekly");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const target = await createMonitorTarget({
        name: name.trim(),
        platform,
        accountHandle: accountHandle.trim() || undefined,
        queryText: queryText.trim(),
        cadence,
        notes: notes.trim() || undefined,
      });
      setMessage(`Saved monitor target "${target.name}" on ${target.platform}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create monitor target.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Competitor monitor</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Create a recurring monitoring target.</h2>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Target name</span>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Creator growth pulse"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Platform</span>
          <select
            value={platform}
            onChange={(event) => setPlatform(event.target.value as MonitorPlatform)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          >
            {platformOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Cadence</span>
          <select
            value={cadence}
            onChange={(event) => setCadence(event.target.value as MonitorCadence)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          >
            {cadenceOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Account handle</span>
          <input
            value={accountHandle}
            onChange={(event) => setAccountHandle(event.target.value)}
            placeholder="@competitor"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Query text</span>
          <input
            value={queryText}
            onChange={(event) => setQueryText(event.target.value)}
            placeholder="creator growth"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Notes</span>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={3}
          placeholder="What should this monitor keep an eye on?"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">Handles and freeform queries can be combined for one target.</p>
        <button
          type="submit"
          disabled={isSaving}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSaving ? "Saving..." : "Create target"}
        </button>
      </div>
      {message ? <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</p> : null}
    </form>
  );
}
