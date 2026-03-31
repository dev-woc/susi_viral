import {
  PLATFORM_VALUES,
  TIMEFRAME_VALUES,
  type LibraryFilters,
  type Platform,
  type SearchRequest,
  type Timeframe,
} from "@/lib/types";

export type SearchParamsInput = Record<string, string | string[] | undefined>;

const DEFAULT_TIMEFRAME: Timeframe = "7d";
const DEFAULT_THRESHOLD = 70;

function pickFirst(value: string | string[] | undefined): string {
  if (Array.isArray(value)) {
    return value[0] ?? "";
  }

  return value ?? "";
}

function parseNumber(value: string | string[] | undefined, fallback: number): number {
  const numeric = Number(pickFirst(value));
  if (Number.isFinite(numeric)) {
    return Math.min(100, Math.max(0, numeric));
  }

  return fallback;
}

function normalizePlatforms(value: string | string[] | undefined): Platform[] {
  const rawValues = Array.isArray(value)
    ? value
    : typeof value === "string" && value.includes(",")
      ? value.split(",")
      : value
        ? [value]
        : [];

  const normalized = rawValues
    .map((candidate) => candidate.trim())
    .filter((candidate): candidate is Platform =>
      (PLATFORM_VALUES as readonly string[]).includes(candidate)
    );

  return normalized.length > 0 ? normalized : [...PLATFORM_VALUES];
}

function parseTimeframe(value: string | string[] | undefined): Timeframe {
  const candidate = pickFirst(value);
  if ((TIMEFRAME_VALUES as readonly string[]).includes(candidate)) {
    return candidate as Timeframe;
  }

  return DEFAULT_TIMEFRAME;
}

export function parseSearchParams(params: SearchParamsInput = {}): SearchRequest {
  return {
    query: pickFirst(params.query ?? params.q).trim(),
    platforms: normalizePlatforms(params.platform ?? params.platforms),
    timeframe: parseTimeframe(params.timeframe),
    minVirality: parseNumber(params.minVirality ?? params.threshold, DEFAULT_THRESHOLD),
  };
}

export function buildSearchPath(filters: SearchRequest): string {
  const searchParams = new URLSearchParams();
  searchParams.set("q", filters.query);
  searchParams.set("timeframe", filters.timeframe);
  searchParams.set("minVirality", String(filters.minVirality));
  searchParams.set("platforms", filters.platforms.join(","));

  return `/search?${searchParams.toString()}`;
}

export function buildLibraryPath(filters: LibraryFilters): string {
  const searchParams = new URLSearchParams();

  if (filters.platform && filters.platform !== "all") {
    searchParams.set("platform", filters.platform);
  }

  if (filters.hook && filters.hook !== "all") {
    searchParams.set("hook", filters.hook);
  }

  const query = searchParams.toString();
  return query ? `/library?${query}` : "/library";
}
