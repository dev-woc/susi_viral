import { buildUrl } from "@/lib/backend";

export type Workspace = {
  id: number;
  slug: string;
  name: string;
  createdAt: string;
  memberCount: number;
  isActive: boolean;
};

export type MonitorPlatform = "tiktok" | "youtube_shorts" | "instagram_reels" | "twitter_x" | "reddit";
export type MonitorCadence = "daily" | "weekly" | "custom";

export type WorkspaceSummary = {
  items: Workspace[];
  activeWorkspaceId: number | null;
};

export type MonitorTarget = {
  id: string;
  targetId: string;
  workspaceId: number;
  name: string;
  platform: MonitorPlatform;
  accountHandle: string | null;
  queryText: string;
  cadence: MonitorCadence;
  enabled: boolean;
  notes: string | null;
  lastRunAt: string | null;
  createdAt: string;
};

export type WorkspaceSwitchInput = {
  workspaceSlug: string;
  workspaceName?: string;
};

export type MonitorTargetInput = {
  name: string;
  platform: MonitorPlatform;
  accountHandle?: string;
  queryText: string;
  cadence: MonitorCadence;
  enabled?: boolean;
  notes?: string;
};

const DEFAULT_WORKSPACES: WorkspaceSummary = {
  activeWorkspaceId: 1,
  items: [
    {
      id: 1,
      slug: "personal",
      name: "Personal Workspace",
      createdAt: "2026-03-28T12:00:00Z",
      memberCount: 1,
      isActive: true,
    },
  ],
};

const DEFAULT_MONITOR_TARGETS: MonitorTarget[] = [
  {
    id: "1",
    targetId: "target_local_01",
    workspaceId: 1,
    name: "Creator growth monitor",
    platform: "tiktok",
    accountHandle: "@competitor",
    queryText: "creator growth",
    cadence: "weekly",
    enabled: true,
    notes: "Local fallback target",
    lastRunAt: null,
    createdAt: "2026-03-30T12:00:00Z",
  },
];

function normalizeWorkspace(payload: {
  id: number;
  slug: string;
  name: string;
  created_at: string;
  member_count: number;
  is_active: boolean;
}): Workspace {
  return {
    id: payload.id,
    slug: payload.slug,
    name: payload.name,
    createdAt: payload.created_at,
    memberCount: payload.member_count,
    isActive: payload.is_active,
  };
}

function normalizeMonitorTarget(payload: {
  id: number;
  target_id: string;
  workspace_id: number;
  name: string;
  platform: MonitorPlatform;
  account_handle?: string | null;
  query_text: string;
  cadence: MonitorCadence;
  enabled: boolean;
  notes?: string | null;
  last_run_at?: string | null;
  created_at: string;
}): MonitorTarget {
  return {
    id: String(payload.id),
    targetId: payload.target_id,
    workspaceId: payload.workspace_id,
    name: payload.name,
    platform: payload.platform,
    accountHandle: payload.account_handle ?? null,
    queryText: payload.query_text,
    cadence: payload.cadence,
    enabled: payload.enabled,
    notes: payload.notes ?? null,
    lastRunAt: payload.last_run_at ?? null,
    createdAt: payload.created_at,
  };
}

export async function listWorkspaces(): Promise<WorkspaceSummary> {
  const endpoint = buildUrl("/api/workspaces");
  if (!endpoint) {
    return DEFAULT_WORKSPACES;
  }

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Workspace lookup failed with ${response.status}`);
    }
    const payload = (await response.json()) as {
      items: Array<Parameters<typeof normalizeWorkspace>[0]>;
      active_workspace_id: number | null;
    };
    return {
      items: payload.items.map(normalizeWorkspace),
      activeWorkspaceId: payload.active_workspace_id,
    };
  } catch {
    return DEFAULT_WORKSPACES;
  }
}

export async function switchWorkspace(input: WorkspaceSwitchInput): Promise<Workspace> {
  const endpoint = buildUrl("/api/workspaces/switch");
  if (!endpoint) {
    return {
      id: Date.now(),
      slug: input.workspaceSlug,
      name: input.workspaceName ?? input.workspaceSlug,
      createdAt: new Date().toISOString(),
      memberCount: 1,
      isActive: true,
    };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      workspace_slug: input.workspaceSlug,
      workspace_name: input.workspaceName,
    }),
  });

  if (!response.ok) {
    throw new Error(`Workspace switch failed with ${response.status}`);
  }

  const payload = (await response.json()) as { workspace: Parameters<typeof normalizeWorkspace>[0] };
  return normalizeWorkspace(payload.workspace);
}

export async function listMonitorTargets(): Promise<MonitorTarget[]> {
  const endpoint = buildUrl("/api/monitor-targets");
  if (!endpoint) {
    return DEFAULT_MONITOR_TARGETS;
  }

  try {
    const response = await fetch(endpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Monitor target lookup failed with ${response.status}`);
    }
    const payload = (await response.json()) as {
      items: Array<Parameters<typeof normalizeMonitorTarget>[0]>;
    };
    return payload.items.map(normalizeMonitorTarget);
  } catch {
    return DEFAULT_MONITOR_TARGETS;
  }
}

export async function createMonitorTarget(input: MonitorTargetInput): Promise<MonitorTarget> {
  const endpoint = buildUrl("/api/monitor-targets");
  if (!endpoint) {
    return {
      id: String(Date.now()),
      targetId: `target_${Date.now()}`,
      workspaceId: DEFAULT_WORKSPACES.activeWorkspaceId ?? 1,
      name: input.name,
      platform: input.platform,
      accountHandle: input.accountHandle ?? null,
      queryText: input.queryText,
      cadence: input.cadence,
      enabled: input.enabled ?? true,
      notes: input.notes ?? null,
      lastRunAt: null,
      createdAt: new Date().toISOString(),
    };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: input.name,
      platform: input.platform,
      account_handle: input.accountHandle,
      query_text: input.queryText,
      cadence: input.cadence,
      enabled: input.enabled ?? true,
      notes: input.notes,
    }),
  });

  if (!response.ok) {
    throw new Error(`Monitor target create failed with ${response.status}`);
  }

  return normalizeMonitorTarget((await response.json()) as Parameters<typeof normalizeMonitorTarget>[0]);
}
