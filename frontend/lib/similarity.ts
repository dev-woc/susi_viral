import { demoLibraryItems } from "@/lib/mock-data";
import type { ContentDNA, Platform } from "@/lib/types";
import { buildUrl, normalizeContentDna } from "@/lib/backend";

export type SimilarityResult = {
  contentDnaId: number;
  score: number;
  matchedOn: string;
  contentDna: ContentDNA;
};

export type SimilaritySearchResult = {
  items: SimilarityResult[];
  query: string;
  provider: string;
  generatedAt: string;
};

export type SimilaritySearchInput = {
  query: string;
  limit?: number;
  platform?: Platform | "all";
};

const DEFAULT_SIMILARITY_RESULTS: SimilaritySearchResult = {
  query: "creator growth hooks",
  provider: "local-fallback",
  generatedAt: "2026-03-30T12:00:00Z",
  items: demoLibraryItems
    .map((item, index) => ({
      contentDnaId: item.content_dna.id ?? index + 1,
      score: Math.max(0.72 - index * 0.08, 0.45),
      matchedOn: "semantic-query",
      contentDna: item.content_dna,
    }))
    .slice(0, 2),
};

function normalizeSimilarityResponse(payload: {
  items: Array<{
    content_dna_id: number;
    score: number;
    matched_on: string;
    content_dna: Record<string, unknown>;
  }>;
  query: string;
  provider: string;
  generated_at: string;
}): SimilaritySearchResult {
  return {
    query: payload.query,
    provider: payload.provider,
    generatedAt: payload.generated_at,
    items: payload.items.map((item) => ({
      contentDnaId: item.content_dna_id,
      score: item.score,
      matchedOn: item.matched_on,
      contentDna: normalizeContentDna(item.content_dna as never),
    })),
  };
}

export function buildSimilarityPath(
  clipId: number | string,
  filters: { query?: string; platform?: Platform | "all"; limit?: number } = {},
): string {
  const params = new URLSearchParams();
  if (filters.query?.trim()) {
    params.set("q", filters.query.trim());
  }
  if (filters.platform && filters.platform !== "all") {
    params.set("platform", filters.platform);
  }
  if (filters.limit) {
    params.set("limit", String(filters.limit));
  }
  const query = params.toString();
  return query ? `/library/similar/${clipId}?${query}` : `/library/similar/${clipId}`;
}

export async function searchSimilarity(input: SimilaritySearchInput): Promise<SimilaritySearchResult> {
  const endpoint = buildUrl("/api/similarity/search");
  if (!endpoint) {
    return DEFAULT_SIMILARITY_RESULTS;
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: input.query,
        limit: input.limit ?? 5,
        platform: input.platform && input.platform !== "all" ? input.platform : undefined,
      }),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Similarity search failed with ${response.status}`);
    }

    return normalizeSimilarityResponse((await response.json()) as Parameters<typeof normalizeSimilarityResponse>[0]);
  } catch {
    return DEFAULT_SIMILARITY_RESULTS;
  }
}

export async function listSimilarClips(contentDnaId: number, limit = 5): Promise<SimilaritySearchResult> {
  const endpoint = buildUrl(`/api/similarity/clips/${contentDnaId}?limit=${limit}`);
  if (!endpoint) {
    return {
      ...DEFAULT_SIMILARITY_RESULTS,
      query: `content_dna:${contentDnaId}`,
      items: DEFAULT_SIMILARITY_RESULTS.items.slice(0, limit),
    };
  }

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Similarity lookup failed with ${response.status}`);
    }

    return normalizeSimilarityResponse((await response.json()) as Parameters<typeof normalizeSimilarityResponse>[0]);
  } catch {
    return {
      ...DEFAULT_SIMILARITY_RESULTS,
      query: `content_dna:${contentDnaId}`,
      items: DEFAULT_SIMILARITY_RESULTS.items.slice(0, limit),
    };
  }
}
