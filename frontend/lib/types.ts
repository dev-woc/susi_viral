export type Platform = "tiktok" | "youtube_shorts";

export type Timeframe = "24h" | "7d" | "30d" | "all";

export const PLATFORM_VALUES = ["tiktok", "youtube_shorts"] as const satisfies readonly Platform[];
export const TIMEFRAME_VALUES = ["24h", "7d", "30d", "all"] as const satisfies readonly Timeframe[];

export type SearchTimeframe = Timeframe;

export interface ContentDNA {
  schema_version: string;
  clip_id: string;
  source_url: string;
  platform: Platform;
  virality_score: number;
  posted_at: string;
  niche: string | null;
  hook: string | null;
  format: string | null;
  emotion: string | null;
  structure: string | null;
  cta: string | null;
  replication_notes: string | null;
  pattern_tags: string[];
}

export interface SearchClip {
  id: string;
  title: string;
  platform: Platform;
  creator: string;
  thumbnail_url: string;
  summary: string;
  content_dna: ContentDNA;
  saved: boolean;
}

export interface PlatformFailure {
  platform: Platform;
  message: string;
}

export interface SearchResponse {
  search_id: string;
  query: string;
  timeframe: Timeframe;
  min_virality: number;
  results: SearchClip[];
  partial_failures: PlatformFailure[];
  total_results: number;
  generated_at: string;
}

export interface SearchRequest {
  query: string;
  platforms: Platform[];
  timeframe: Timeframe;
  minVirality: number;
}

export interface LibraryItem {
  id: string;
  saved_at: string;
  notes: string | null;
  content_dna: ContentDNA;
  title: string;
  creator: string;
  thumbnail_url: string;
  platform: Platform;
}

export interface LibraryResponse {
  items: LibraryItem[];
  filters: {
    platform: Platform | "all";
    hook: string | "all";
  };
}

export interface LibraryFilters {
  platform?: Platform | "all";
  hook?: string | "all";
}
