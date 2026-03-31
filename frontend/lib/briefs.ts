import { demoLibraryItems } from "@/lib/mock-data";
import type { ContentDNA } from "@/lib/types";
import { buildUrl, normalizeContentDna } from "@/lib/backend";

export type ContentBrief = {
  id: string;
  briefId: string;
  title: string;
  objective: string;
  audience: string;
  tone: string | null;
  summary: string;
  recommendedShots: string[];
  selectedContentDnaIds: number[];
  patternTags: string[];
  createdAt: string;
  updatedAt: string;
  selectedClips: ContentDNA[];
};

export type ContentBriefCreateInput = {
  title: string;
  objective: string;
  audience: string;
  selectedContentDnaIds: number[];
  reportRunId?: number;
  tone?: string;
  notes?: string;
};

const DEFAULT_BRIEFS: ContentBrief[] = [
  {
    id: "brief_local_01",
    briefId: "brief_local_01",
    title: "Creator growth quick-hit brief",
    objective: "Turn pattern research into a one-take planning draft.",
    audience: "solo creators shipping weekly shorts",
    tone: "direct",
    summary: "Lead with a clear promise, prove it quickly, and end with a low-friction CTA.",
    recommendedShots: [
      "Open on the payoff before any setup.",
      "Use one visual proof moment in the first five seconds.",
      "Close with a save or comment CTA.",
    ],
    selectedContentDnaIds: demoLibraryItems
      .map((item) => item.content_dna.id)
      .filter((value): value is number => typeof value === "number"),
    patternTags: ["hook-proof", "save-worthy", "quick-cut"],
    createdAt: "2026-03-30T12:00:00Z",
    updatedAt: "2026-03-30T12:00:00Z",
    selectedClips: demoLibraryItems.map((item) => item.content_dna),
  },
];

function normalizeBrief(payload: {
  id: number;
  brief_id: string;
  title: string;
  objective: string;
  audience: string;
  tone?: string | null;
  summary: string;
  recommended_shots: string[];
  selected_content_dna_ids: number[];
  pattern_tags: string[];
  created_at: string;
  updated_at: string;
  selected_clips: Array<Record<string, unknown>>;
}): ContentBrief {
  return {
    id: String(payload.id),
    briefId: payload.brief_id,
    title: payload.title,
    objective: payload.objective,
    audience: payload.audience,
    tone: payload.tone ?? null,
    summary: payload.summary,
    recommendedShots: payload.recommended_shots,
    selectedContentDnaIds: payload.selected_content_dna_ids,
    patternTags: payload.pattern_tags,
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
    selectedClips: payload.selected_clips.map((clip) => normalizeContentDna(clip as never)),
  };
}

export async function listBriefs(): Promise<ContentBrief[]> {
  const endpoint = buildUrl("/api/briefs");
  if (!endpoint) {
    return DEFAULT_BRIEFS;
  }

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Brief lookup failed with ${response.status}`);
    }

    const payload = (await response.json()) as { items: Array<Parameters<typeof normalizeBrief>[0]> };
    return payload.items.map(normalizeBrief);
  } catch {
    return DEFAULT_BRIEFS;
  }
}

export async function createBrief(input: ContentBriefCreateInput): Promise<ContentBrief> {
  const endpoint = buildUrl("/api/briefs");
  if (!endpoint) {
    const fallbackId = `brief_${Date.now()}`;
    return {
      id: fallbackId,
      briefId: fallbackId,
      title: input.title,
      objective: input.objective,
      audience: input.audience,
      tone: input.tone ?? null,
      summary: "Local fallback brief created until the backend is available.",
      recommendedShots: [
        "Open with the strongest hook from the selected clips.",
        "Show proof before the midpoint.",
        "End with a CTA aligned to the objective.",
      ],
      selectedContentDnaIds: input.selectedContentDnaIds,
      patternTags: ["local-brief", "fallback"],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      selectedClips: demoLibraryItems
        .filter((item) => item.content_dna.id && input.selectedContentDnaIds.includes(item.content_dna.id))
        .map((item) => item.content_dna),
    };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: input.title,
      objective: input.objective,
      audience: input.audience,
      selected_content_dna_ids: input.selectedContentDnaIds,
      report_run_id: input.reportRunId,
      tone: input.tone,
      notes: input.notes,
    }),
  });

  if (!response.ok) {
    throw new Error(`Brief create failed with ${response.status}`);
  }

  return normalizeBrief((await response.json()) as Parameters<typeof normalizeBrief>[0]);
}
