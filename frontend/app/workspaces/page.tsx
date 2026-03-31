import { MonitorTargetForm } from "@/components/monitor-target-form";
import { MonitorTargetList } from "@/components/monitor-target-list";
import { WorkspaceSwitcher } from "@/components/workspace-switcher";
import { listMonitorTargets, listWorkspaces } from "@/lib/workspaces";

export const dynamic = "force-dynamic";

export default async function WorkspacesPage() {
  const [workspaces, monitorTargets] = await Promise.all([listWorkspaces(), listMonitorTargets()]);
  const activeWorkspace = workspaces.items.find((workspace) => workspace.isActive);

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Phase 3 workspaces</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Manage the team context behind briefs, reports, and monitoring.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
            The backend currently mirrors workspace state directly, so this page gives you a simple control plane before full auth syncing lands.
          </p>
          {activeWorkspace ? (
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
              Active workspace: <span className="text-white">{activeWorkspace.name}</span> ({activeWorkspace.memberCount} member(s))
            </div>
          ) : null}
        </div>
        <WorkspaceSwitcher workspaces={workspaces.items} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <MonitorTargetForm />
        <MonitorTargetList targets={monitorTargets} />
      </section>
    </div>
  );
}
