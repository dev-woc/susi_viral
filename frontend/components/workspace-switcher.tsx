"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { switchWorkspace, type Workspace } from "@/lib/workspaces";

export function WorkspaceSwitcher({ workspaces }: { workspaces: Workspace[] }) {
  const router = useRouter();
  const active = workspaces.find((workspace) => workspace.isActive) ?? workspaces[0];
  const [workspaceSlug, setWorkspaceSlug] = useState(active?.slug ?? "");
  const [workspaceName, setWorkspaceName] = useState(active?.name ?? "");
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage(null);

    try {
      const workspace = await switchWorkspace({
        workspaceSlug: workspaceSlug.trim(),
        workspaceName: workspaceName.trim() || undefined,
      });
      setMessage(`Active workspace is now "${workspace.name}".`);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to switch workspaces.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Workspace context</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Switch or create the active workspace.</h2>
      </div>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Workspace slug</span>
        <input
          value={workspaceSlug}
          onChange={(event) => setWorkspaceSlug(event.target.value)}
          placeholder="personal"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <label className="block">
        <span className="mb-2 block text-sm uppercase tracking-[0.24em] text-slate-400">Workspace name</span>
        <input
          value={workspaceName}
          onChange={(event) => setWorkspaceName(event.target.value)}
          placeholder="Personal Workspace"
          className="w-full rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-amber-400/50 focus:ring-2 focus:ring-amber-500/20"
        />
      </label>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-400">Backend-driven for now; auth syncing can be layered in later.</p>
        <button
          type="submit"
          disabled={isSaving}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSaving ? "Switching..." : "Switch workspace"}
        </button>
      </div>
      {message ? <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{message}</p> : null}
    </form>
  );
}
