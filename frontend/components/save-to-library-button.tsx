"use client";

import { useState } from "react";
import { saveLibraryItem } from "@/lib/api";

interface SaveToLibraryButtonProps {
  clipId: string;
  contentDnaId?: number;
  saved?: boolean;
}

export function SaveToLibraryButton({ clipId, contentDnaId, saved = false }: SaveToLibraryButtonProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(saved);

  async function handleSave() {
    setIsSaving(true);
    try {
      await saveLibraryItem(contentDnaId ? { clipId, contentDnaId } : { clipId });
      setIsSaved(true);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <button
      type="button"
      disabled={isSaving || isSaved}
      onClick={handleSave}
      className={`inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-medium transition ${
        isSaved
          ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-100"
          : "border-white/10 bg-white/5 text-slate-200 hover:border-amber-400/40 hover:bg-white/10"
      }`}
    >
      {isSaved ? "Saved" : isSaving ? "Saving..." : "Save to library"}
    </button>
  );
}
