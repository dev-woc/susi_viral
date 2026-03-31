"use client";

import { useState, type FormEvent } from "react";
import { createBrief } from "@/lib/briefs";

type ContentBriefBuilderProps = {
  initialSelectedContentDnaIds?: number[];
};

export function ContentBriefBuilder({ initialSelectedContentDnaIds = [] }: ContentBriefBuilderProps) {
  const [title, setTitle] = useState("");
  const [objective, setObjective] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedIds, setSelectedIds] = useState(initialSelectedContentDnaIds.join(", "));
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const brief = await createBrief({
        title: title.trim() || "Untitled brief",
        objective: objective.trim(),
        audience: audience.trim(),
        tone: tone.trim() || undefined,
        notes: notes.trim() || undefined,
        selectedContentDnaIds: selectedIds
          .split(",")
          .map((value) => Number(value.trim()))
          .filter((value) => Number.isInteger(value) && value > 0),
      });

      setMessage(`Saved brief "${brief.title}" with ${brief.selectedContentDnaIds.length} selected clip(s).`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to save brief.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Content brief</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Turn saved patterns into a usable shooting plan.</h2>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Title</span>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Creator growth sprint brief"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Objective</span>
          <input
            value={objective}
            onChange={(event) => setObjective(event.target.value)}
            placeholder="Increase saves on weekly creator tips"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Audience</span>
          <input
            value={audience}
            onChange={(event) => setAudience(event.target.value)}
            placeholder="Solo creators"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Tone</span>
          <input
            value={tone}
            onChange={(event) => setTone(event.target.value)}
            placeholder="direct, calm, high-energy"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Selected clip ids</span>
          <input
            aria-label="Selected clip ids"
            value={selectedIds}
            onChange={(event) => setSelectedIds(event.target.value)}
            placeholder="101, 102"
            className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
          />
        </label>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Notes</span>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Call out patterns or constraints the brief should preserve."
          rows={4}
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-400">Use comma-separated `content_dna` ids from the library or similar-clips views.</p>
        <button
          type="submit"
          disabled={isSaving}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-6 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSaving ? "Saving..." : "Create brief"}
        </button>
      </div>
      {message ? <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</p> : null}
    </form>
  );
}
