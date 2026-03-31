import { demoLibraryItems, demoSearchResponse } from "@/lib/mock-data";
import type {
  LibraryItem,
  LibraryResponse,
  Platform,
  SearchRequest,
  SearchResponse,
  Timeframe,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function buildUrl(path: string) {
  if (!API_BASE_URL) {
    return path;
  }

  return new URL(path, API_BASE_URL).toString();
}

async function safeJson<T>(response: Response): Promise<T> {
  return (await response.json()) as T;
}

export async function searchClips(request: SearchRequest): Promise<SearchResponse> {
  if (!API_BASE_URL) {
    return {
      ...demoSearchResponse,
      query: request.query || demoSearchResponse.query,
      timeframe: request.timeframe,
      min_virality: request.minVirality,
    };
  }

  try {
    const response = await fetch(buildUrl("/api/search"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Search failed with ${response.status}`);
    }

    return await safeJson<SearchResponse>(response);
  } catch {
    return {
      ...demoSearchResponse,
      query: request.query || demoSearchResponse.query,
      timeframe: request.timeframe,
      min_virality: request.minVirality,
    };
  }
}

export async function listLibraryItems(filters?: {
  platform?: Platform | "all";
  hook?: string | "all";
}): Promise<LibraryResponse> {
  if (!API_BASE_URL) {
    return {
      items: demoLibraryItems,
      filters: {
        platform: filters?.platform ?? "all",
        hook: filters?.hook ?? "all",
      },
    };
  }

  const searchParams = new URLSearchParams();
  if (filters?.platform && filters.platform !== "all") {
    searchParams.set("platform", filters.platform);
  }
  if (filters?.hook && filters.hook !== "all") {
    searchParams.set("hook", filters.hook);
  }

  try {
    const response = await fetch(buildUrl(`/api/library/items?${searchParams.toString()}`), {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Library lookup failed with ${response.status}`);
    }

    return await safeJson<LibraryResponse>(response);
  } catch {
    return {
      items: demoLibraryItems,
      filters: {
        platform: filters?.platform ?? "all",
        hook: filters?.hook ?? "all",
      },
    };
  }
}

export async function saveLibraryItem(input: {
  clipId: string;
  notes?: string;
}): Promise<LibraryItem> {
  if (!API_BASE_URL) {
    const source = demoSearchResponse.results.find((clip) => clip.id === input.clipId) ?? demoSearchResponse.results[0];

    return {
      id: `lib_${input.clipId}`,
      saved_at: new Date().toISOString(),
      notes: input.notes ?? "Saved from frontend scaffold",
      title: source.title,
      creator: source.creator,
      thumbnail_url: source.thumbnail_url,
      platform: source.platform,
      content_dna: source.content_dna,
    };
  }

  try {
    const response = await fetch(buildUrl("/api/library/items"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Save failed with ${response.status}`);
    }

    return await safeJson<LibraryItem>(response);
  } catch {
    const source = demoSearchResponse.results.find((clip) => clip.id === input.clipId) ?? demoSearchResponse.results[0];
    return {
      id: `lib_${input.clipId}`,
      saved_at: new Date().toISOString(),
      notes: input.notes ?? "Saved from frontend scaffold",
      title: source.title,
      creator: source.creator,
      thumbnail_url: source.thumbnail_url,
      platform: source.platform,
      content_dna: source.content_dna,
    };
  }
}

export function parsePlatformParam(value: string | string[] | undefined): Platform[] {
  const values = Array.isArray(value) ? value : value ? value.split(",") : [];
  const allowed: Platform[] = [];

  for (const entry of values) {
    if (entry === "tiktok" || entry === "youtube_shorts") {
      allowed.push(entry);
    }
  }

  return allowed.length > 0 ? allowed : ["tiktok", "youtube_shorts"];
}

export function parseTimeframeParam(value: string | string[] | undefined): Timeframe {
  const candidate = Array.isArray(value) ? value[0] : value;
  if (candidate === "24h" || candidate === "7d" || candidate === "30d" || candidate === "all") {
    return candidate;
  }
  return "7d";
}
