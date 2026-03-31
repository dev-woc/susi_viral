import type { Platform, ContentDNA } from "@/lib/types";
import { buildUrl, getApiOrigin } from "@/lib/backend";

export type ReportCadence = "daily" | "weekly" | "custom";
export type DeliveryChannel = "dashboard" | "email" | "pdf";
export type ReportStatus = "scheduled" | "running" | "partial" | "complete" | "failed";

export type ReportDefinition = {
  id: string;
  backend_id?: number;
  name: string;
  query: string;
  platforms: Platform[];
  cadence: ReportCadence;
  topN: number;
  deliveryChannels: DeliveryChannel[];
  last_run_at: string | null;
  next_run_at: string | null;
  status: ReportStatus;
  pattern_summary: string;
  pattern_deltas?: Record<string, number>;
};

export type ReportRun = {
  id: string;
  report_id: string;
  started_at: string;
  finished_at: string | null;
  status: ReportStatus;
  result_count: number;
  delivery_targets: DeliveryChannel[];
  notes: string;
  pattern_deltas?: Record<string, number>;
};

export type ReportSummary = {
  reports: ReportDefinition[];
  recent_runs: ReportRun[];
};

export type ReportSearchParams = Record<string, string | string[] | undefined>;

const DEFAULT_REPORTS: ReportDefinition[] = [
  {
    id: "report_01",
    name: "Weekly fitness pattern scan",
    query: "fitness meal prep",
    platforms: ["tiktok", "youtube_shorts"],
    cadence: "weekly",
    topN: 10,
    deliveryChannels: ["dashboard", "email"],
    last_run_at: "2026-03-29T09:00:00Z",
    next_run_at: "2026-04-05T09:00:00Z",
    status: "scheduled",
    pattern_summary: "Two-thirds of clips use a question hook plus quick reveal.",
  },
  {
    id: "report_02",
    name: "Daily creator research pulse",
    query: "creator growth",
    platforms: ["tiktok"],
    cadence: "daily",
    topN: 5,
    deliveryChannels: ["dashboard"],
    last_run_at: "2026-03-30T07:15:00Z",
    next_run_at: "2026-03-31T07:15:00Z",
    status: "partial",
    pattern_summary: "Strongest clips rely on direct CTA and fast-cut pacing.",
  },
];

const DEFAULT_RUNS: ReportRun[] = [
  {
    id: "run_01",
    report_id: "report_01",
    started_at: "2026-03-29T09:00:00Z",
    finished_at: "2026-03-29T09:41:00Z",
    status: "complete",
    result_count: 10,
    delivery_targets: ["dashboard", "email"],
    notes: "Delivered on schedule with all channels successful.",
  },
  {
    id: "run_02",
    report_id: "report_02",
    started_at: "2026-03-30T07:15:00Z",
    finished_at: "2026-03-30T07:21:00Z",
    status: "partial",
    result_count: 5,
    delivery_targets: ["dashboard"],
    notes: "TikTok connector degraded, but dashboard snapshot was stored.",
  },
];

export function parseReportSearchParams(params: ReportSearchParams = {}): {
  cadence: ReportCadence | "all";
  platform: Platform | "all";
} {
  const cadence = typeof params.cadence === "string" ? params.cadence : Array.isArray(params.cadence) ? params.cadence[0] : undefined;
  const platform = typeof params.platform === "string" ? params.platform : Array.isArray(params.platform) ? params.platform[0] : undefined;

  return {
    cadence: cadence === "daily" || cadence === "weekly" || cadence === "custom" ? cadence : "all",
    platform: platform === "tiktok" || platform === "youtube_shorts" ? platform : "all",
  };
}

export function buildReportsPath(filters: { cadence?: ReportCadence | "all"; platform?: Platform | "all" } = {}): string {
  const params = new URLSearchParams();

  if (filters.cadence && filters.cadence !== "all") {
    params.set("cadence", filters.cadence);
  }

  if (filters.platform && filters.platform !== "all") {
    params.set("platform", filters.platform);
  }

  const query = params.toString();
  return query ? `/reports?${query}` : "/reports";
}

export async function listReports(): Promise<ReportSummary> {
  const endpoint = buildUrl("/api/reports");

  if (!endpoint) {
    return {
      reports: DEFAULT_REPORTS,
      recent_runs: DEFAULT_RUNS,
    };
  }

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Reports lookup failed with ${response.status}`);
    }
    const payload = (await response.json()) as {
      items: Array<{
        id: number;
        report_id: string;
        name: string;
        query_text: string;
        platforms: Platform[];
        cadence: ReportCadence;
        result_limit: number;
        delivery_channels: DeliveryChannel[];
        last_run_at: string | null;
        next_run_at: string | null;
        latest_run: {
          report_run_id: string;
          created_at: string;
          completed_at: string | null;
          status: ReportStatus;
          total_ranked: number;
          deliveries: Array<{ channel: DeliveryChannel }>;
          pattern_deltas: Record<string, number>;
          pattern_summary: Record<string, number>;
        } | null;
      }>;
    };

    const reports = payload.items.map((report) => ({
      id: report.report_id,
      backend_id: report.id,
      name: report.name,
      query: report.query_text,
      platforms: report.platforms.filter(
        (platform): platform is Platform => platform === "tiktok" || platform === "youtube_shorts",
      ),
      cadence: report.cadence,
      topN: report.result_limit,
      deliveryChannels: report.delivery_channels,
      last_run_at: report.last_run_at,
      next_run_at: report.next_run_at,
      status: report.latest_run?.status ?? "scheduled",
      pattern_summary: summarizePatternSummary(report.latest_run?.pattern_summary ?? {}),
      pattern_deltas: report.latest_run?.pattern_deltas ?? {},
    }));

    const recent_runs = payload.items
      .flatMap((report) => {
        if (!report.latest_run) {
          return [];
        }

        return [
          {
            id: report.latest_run.report_run_id,
            report_id: report.report_id,
            started_at: report.latest_run.created_at,
            finished_at: report.latest_run.completed_at,
            status: report.latest_run.status,
            result_count: report.latest_run.total_ranked,
            delivery_targets:
              report.latest_run.deliveries.length > 0
                ? report.latest_run.deliveries.map((delivery) => delivery.channel)
                : report.delivery_channels,
            notes: summarizePatternSummary(report.latest_run.pattern_summary),
            pattern_deltas: report.latest_run.pattern_deltas,
          },
        ];
      })
      .sort((left, right) => right.started_at.localeCompare(left.started_at));

    return { reports, recent_runs };
  } catch {
    return {
      reports: DEFAULT_REPORTS,
      recent_runs: DEFAULT_RUNS,
    };
  }
}

export async function createReportDefinition(input: {
  name: string;
  query: string;
  platforms: Platform[];
  cadence: ReportCadence;
  topN: number;
  deliveryChannels: DeliveryChannel[];
}): Promise<ReportDefinition> {
  const endpoint = buildUrl("/api/reports");

  if (!endpoint) {
    return {
      id: `report_${Date.now()}`,
      ...input,
      last_run_at: null,
      next_run_at: null,
      status: "scheduled",
      pattern_summary: "Draft report created locally until backend wiring is available.",
    };
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: input.name,
        query_text: input.query,
        platforms: input.platforms,
        timeframe: "7d",
        minimum_virality_score: 50,
        result_limit: input.topN,
        cadence: input.cadence,
        delivery_channels: input.deliveryChannels,
        enabled: true,
      }),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Report create failed with ${response.status}`);
    }

    const report = (await response.json()) as {
      id: number;
      report_id: string;
      name: string;
      query_text: string;
      platforms: Platform[];
      cadence: ReportCadence;
      result_limit: number;
      delivery_channels: DeliveryChannel[];
      last_run_at: string | null;
      next_run_at: string | null;
    };

    return {
      id: report.report_id,
      backend_id: report.id,
      name: report.name,
      query: report.query_text,
      platforms: report.platforms.filter(
        (platform): platform is Platform => platform === "tiktok" || platform === "youtube_shorts",
      ),
      cadence: report.cadence,
      topN: report.result_limit,
      deliveryChannels: report.delivery_channels,
      last_run_at: report.last_run_at,
      next_run_at: report.next_run_at,
      status: "scheduled",
      pattern_summary: "Scheduled report created from the backend.",
    };
  } catch {
    return {
      id: `report_${Date.now()}`,
      ...input,
      last_run_at: null,
      next_run_at: null,
      status: "scheduled",
      pattern_summary: "Draft report created locally until backend wiring is available.",
    };
  }
}

export type ReportPreview = {
  name: string;
  query: string;
  cadence: ReportCadence;
  topN: number;
  deliveryChannels: DeliveryChannel[];
};

export function buildReportPreview(initial: Partial<ReportPreview> = {}): ReportPreview {
  return {
    name: initial.name ?? "Untitled report",
    query: initial.query ?? "",
    cadence: initial.cadence ?? "weekly",
    topN: initial.topN ?? 10,
    deliveryChannels: initial.deliveryChannels ?? ["dashboard"],
  };
}

export function summarizeContentDna(contentDna: ContentDNA): string {
  const format = contentDna.format ?? "unspecified format";
  const hook = contentDna.hook ?? "unspecified hook";
  return `${hook} • ${format}`;
}

function summarizePatternSummary(summary: Record<string, number>): string {
  const entries = Object.entries(summary)
    .sort((left, right) => right[1] - left[1])
    .slice(0, 3);

  if (entries.length === 0) {
    return "No pattern summary available yet.";
  }

  return entries.map(([key, value]) => `${key} (${value})`).join(", ");
}
