import type { ContentDNA, LibraryItem, Platform, SearchClip, SearchResponse, Timeframe } from "@/lib/types";

const FALLBACK_THUMBNAIL = "https://images.unsplash.com/photo-1547592180-85f173990554?w=900";

type BackendPatternTag = {
  name: string;
  category?: string | null;
};

type BackendContentDNA = {
  id?: number;
  raw_clip_id?: number;
  schema_version?: string;
  clip_id: string;
  source_url: string;
  platform: Platform;
  virality_score: number;
  posted_at?: string | null;
  niche?: string | null;
  hook?: string | null;
  format?: string | null;
  emotion?: string | null;
  structure?: string | null;
  cta?: string | null;
  replication_notes?: string | null;
  pattern_tags?: Array<string | BackendPatternTag>;
  confidence?: number;
};

type BackendRawClip = {
  id?: number;
  platform: Platform;
  source_url: string;
  title: string;
  description?: string | null;
  author_name?: string | null;
  author_handle?: string | null;
  raw_payload?: {
    thumbnail_url?: string | null;
  } | null;
  content_dna?: BackendContentDNA | null;
};

type BackendRankedSearchResult = {
  raw_clip: BackendRawClip;
  content_dna?: BackendContentDNA | null;
};

type BackendSearchResponse = {
  search_id: string;
  query: string;
  timeframe: Timeframe;
  minimum_virality_score: number;
  results: BackendRankedSearchResult[];
  platform_failures?: Array<{ platform: Platform; message: string }>;
  summary?: { total_ranked?: number };
  completed_at?: string | null;
  created_at?: string;
};

type BackendLibraryItem = {
  id: number;
  workspace_id: number;
  content_dna_id: number;
  note?: string | null;
  created_at: string;
  content_dna: BackendContentDNA;
  raw_clip?: BackendRawClip | null;
};

export function getApiOrigin(): string | null {
  return process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? null;
}

export function buildUrl(path: string): string | null {
  const origin = getApiOrigin();
  return origin ? new URL(path, origin).toString() : null;
}

function normalizePatternTags(tags: Array<string | BackendPatternTag> | undefined): string[] {
  return (tags ?? []).map((tag) => (typeof tag === "string" ? tag : tag.name));
}

export function normalizeContentDna(contentDna: BackendContentDNA): ContentDNA {
  return {
    id: contentDna.id,
    raw_clip_id: contentDna.raw_clip_id,
    schema_version: contentDna.schema_version ?? "1.0",
    clip_id: contentDna.clip_id,
    source_url: contentDna.source_url,
    platform: contentDna.platform,
    virality_score: contentDna.virality_score,
    posted_at: contentDna.posted_at ?? new Date().toISOString(),
    niche: contentDna.niche ?? null,
    hook: contentDna.hook ?? null,
    format: contentDna.format ?? null,
    emotion: contentDna.emotion ?? null,
    structure: contentDna.structure ?? null,
    cta: contentDna.cta ?? null,
    replication_notes: contentDna.replication_notes ?? null,
    pattern_tags: normalizePatternTags(contentDna.pattern_tags),
    confidence: contentDna.confidence,
  };
}

export function normalizeLibraryItem(item: BackendLibraryItem): LibraryItem {
  const rawClip = item.raw_clip;
  return {
    id: String(item.id),
    workspace_id: item.workspace_id,
    content_dna_id: item.content_dna_id,
    saved_at: item.created_at,
    notes: item.note ?? null,
    title: rawClip?.title ?? item.content_dna.hook ?? item.content_dna.clip_id,
    creator: rawClip?.author_handle ?? rawClip?.author_name ?? "Unknown creator",
    thumbnail_url: rawClip?.raw_payload?.thumbnail_url ?? FALLBACK_THUMBNAIL,
    platform: rawClip?.platform ?? item.content_dna.platform,
    content_dna: normalizeContentDna({
      ...item.content_dna,
      id: item.content_dna.id ?? item.content_dna_id,
    }),
  };
}

export function normalizeSearchResponse(response: BackendSearchResponse): SearchResponse {
  const results: SearchClip[] = response.results.map((result) => {
    const contentDna = normalizeContentDna(
      result.content_dna ?? result.raw_clip.content_dna ?? {
        clip_id: result.raw_clip.source_url,
        source_url: result.raw_clip.source_url,
        platform: result.raw_clip.platform,
        virality_score: 0,
      },
    );

    return {
      id: String(result.raw_clip.id ?? contentDna.id ?? contentDna.clip_id),
      raw_clip_id: result.raw_clip.id,
      content_dna_id: contentDna.id,
      title: result.raw_clip.title,
      platform: result.raw_clip.platform,
      creator: result.raw_clip.author_handle ?? result.raw_clip.author_name ?? "Unknown creator",
      thumbnail_url: result.raw_clip.raw_payload?.thumbnail_url ?? FALLBACK_THUMBNAIL,
      summary:
        result.raw_clip.description ??
        contentDna.replication_notes ??
        contentDna.hook ??
        "Structured clip summary unavailable.",
      content_dna: contentDna,
      saved: false,
    };
  });

  return {
    search_id: response.search_id,
    query: response.query,
    timeframe: response.timeframe,
    min_virality: response.minimum_virality_score,
    results,
    partial_failures: (response.platform_failures ?? []).map((failure) => ({
      platform: failure.platform,
      message: failure.message,
    })),
    total_results: response.summary?.total_ranked ?? results.length,
    generated_at: response.completed_at ?? response.created_at ?? new Date().toISOString(),
  };
}
