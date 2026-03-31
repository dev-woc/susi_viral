import type { LibraryItem, Platform } from "@/lib/types";

export type LibrarySearchParams = Record<string, string | string[] | undefined>;

export type LibraryFilterState = {
  query: string;
  platform: Platform | "all";
  hook: string;
  format: string;
  tag: string;
};

const DEFAULT_FILTER_STATE: LibraryFilterState = {
  query: "",
  platform: "all",
  hook: "",
  format: "",
  tag: "",
};

function getApiOrigin(): string | null {
  return process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? null;
}

function buildUrl(path: string): string | null {
  const origin = getApiOrigin();
  return origin ? new URL(path, origin).toString() : null;
}

export function isLibraryBackendConfigured(): boolean {
  return Boolean(getApiOrigin());
}

export function parseLibrarySearchParams(params: LibrarySearchParams = {}): LibraryFilterState {
  const query = typeof params.q === "string" ? params.q : Array.isArray(params.q) ? params.q[0] ?? "" : "";
  const platform = typeof params.platform === "string" ? params.platform : Array.isArray(params.platform) ? params.platform[0] : undefined;
  const hook = typeof params.hook === "string" ? params.hook : Array.isArray(params.hook) ? params.hook[0] ?? "" : "";
  const format = typeof params.format === "string" ? params.format : Array.isArray(params.format) ? params.format[0] ?? "" : "";
  const tag = typeof params.tag === "string" ? params.tag : Array.isArray(params.tag) ? params.tag[0] ?? "" : "";

  return {
    query,
    platform: platform === "tiktok" || platform === "youtube_shorts" ? platform : "all",
    hook,
    format,
    tag,
  };
}

export function buildLibrarySearchPath(filters: LibraryFilterState): string {
  const params = new URLSearchParams();
  if (filters.query.trim()) {
    params.set("q", filters.query.trim());
  }
  if (filters.platform !== "all") {
    params.set("platform", filters.platform);
  }
  if (filters.hook.trim()) {
    params.set("hook", filters.hook.trim());
  }
  if (filters.format.trim()) {
    params.set("format", filters.format.trim());
  }
  if (filters.tag.trim()) {
    params.set("tag", filters.tag.trim());
  }
  const query = params.toString();
  return query ? `/library/search?${query}` : "/library/search";
}

export function filterLibraryItems(items: LibraryItem[], filters: LibraryFilterState): LibraryItem[] {
  const needle = filters.query.trim().toLowerCase();
  const hookNeedle = filters.hook.trim().toLowerCase();
  const formatNeedle = filters.format.trim().toLowerCase();
  const tagNeedle = filters.tag.trim().toLowerCase();

  return items.filter((item) => {
    if (filters.platform !== "all" && item.platform !== filters.platform) {
      return false;
    }

    if (needle) {
      const haystack = [
        item.title,
        item.creator,
        item.notes ?? "",
        item.content_dna.hook ?? "",
        item.content_dna.format ?? "",
        item.content_dna.replication_notes ?? "",
        item.content_dna.pattern_tags.join(" "),
      ]
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(needle)) {
        return false;
      }
    }

    if (hookNeedle && !(item.content_dna.hook ?? "").toLowerCase().includes(hookNeedle)) {
      return false;
    }

    if (formatNeedle && !(item.content_dna.format ?? "").toLowerCase().includes(formatNeedle)) {
      return false;
    }

    if (tagNeedle && !item.content_dna.pattern_tags.some((tag) => tag.toLowerCase().includes(tagNeedle))) {
      return false;
    }

    return true;
  });
}

export async function listLibrarySearchResults(filters: LibraryFilterState): Promise<LibraryItem[]> {
  const endpoint = buildUrl("/api/library/search");

  if (!endpoint) {
    return filterLibraryItems((await import("@/lib/mock-data")).demoLibraryItems, filters);
  }

  try {
    const response = await fetch(endpoint, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Library search failed with ${response.status}`);
    }

    const payload = (await response.json()) as { items: LibraryItem[] };
    return filterLibraryItems(payload.items, filters);
  } catch {
    const { demoLibraryItems } = await import("@/lib/mock-data");
    return filterLibraryItems(demoLibraryItems, filters);
  }
}

export function defaultLibraryFilters(): LibraryFilterState {
  return { ...DEFAULT_FILTER_STATE };
}
