import type { ReportRun } from "@/lib/reports";

type ReportHistoryTableProps = {
  runs: ReportRun[];
};

function statusClass(status: ReportRun["status"]): string {
  switch (status) {
    case "complete":
      return "border-emerald-400/30 bg-emerald-400/10 text-emerald-100";
    case "partial":
      return "border-amber-400/30 bg-amber-400/10 text-amber-100";
    case "failed":
      return "border-rose-400/30 bg-rose-400/10 text-rose-100";
    default:
      return "border-white/10 bg-white/5 text-slate-200";
  }
}

export function ReportHistoryTable({ runs }: ReportHistoryTableProps) {
  return (
    <section className="space-y-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Report history</p>
          <h2 className="mt-1 text-2xl font-semibold text-white">{runs.length} recent runs</h2>
        </div>
        <p className="text-sm text-slate-400">Each run stores its snapshot so the UI does not recompute history.</p>
      </div>
      <div className="overflow-hidden rounded-3xl border border-white/10">
        <table className="min-w-full divide-y divide-white/10">
          <thead className="bg-white/5 text-left text-xs uppercase tracking-[0.24em] text-slate-400">
            <tr>
              <th className="px-4 py-4 font-medium">Run</th>
              <th className="px-4 py-4 font-medium">Status</th>
              <th className="px-4 py-4 font-medium">Results</th>
              <th className="px-4 py-4 font-medium">Delivery</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {runs.map((run) => (
              <tr key={run.id}>
                <td className="px-4 py-4">
                  <div className="space-y-1">
                    <p className="font-mono text-xs uppercase tracking-[0.24em] text-slate-500">{run.id}</p>
                    <p className="text-sm text-slate-300">
                      Started {new Date(run.started_at).toLocaleString()}
                    </p>
                    <p className="text-sm text-slate-500">{run.notes}</p>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <span className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.24em] ${statusClass(run.status)}`}>
                    {run.status}
                  </span>
                </td>
                <td className="px-4 py-4 text-sm text-slate-300">{run.result_count} ranked clips</td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-2">
                    {run.delivery_targets.map((target) => (
                      <span key={target} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                        {target}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
