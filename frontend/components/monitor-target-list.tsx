import type { MonitorTarget } from "@/lib/workspaces";

export function MonitorTargetList({ targets }: { targets: MonitorTarget[] }) {
  return (
    <section className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Saved targets</p>
          <h2 className="mt-1 text-2xl font-semibold text-white">{targets.length} monitoring target(s)</h2>
        </div>
      </div>
      <div className="grid gap-4">
        {targets.map((target) => (
          <article key={target.targetId} className="rounded-3xl border border-white/10 bg-slate-950/50 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{target.platform.replace("_", " ")}</p>
                <h3 className="text-xl font-semibold text-white">{target.name}</h3>
                <p className="text-sm leading-6 text-slate-300">
                  {target.accountHandle ? `${target.accountHandle} • ` : ""}
                  {target.queryText}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                  {target.cadence}
                </span>
                <span
                  className={`rounded-full border px-3 py-1 text-xs ${
                    target.enabled
                      ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/5 text-slate-300"
                  }`}
                >
                  {target.enabled ? "enabled" : "disabled"}
                </span>
              </div>
            </div>
            {target.notes ? <p className="mt-4 text-sm leading-6 text-slate-400">{target.notes}</p> : null}
          </article>
        ))}
      </div>
    </section>
  );
}
