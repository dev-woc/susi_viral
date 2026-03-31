import Link from "next/link";
import { ReportBuilderForm } from "@/components/report-builder-form";
import { ReportHistoryTable } from "@/components/report-history-table";
import { listReports, parseReportSearchParams } from "@/lib/reports";

export const dynamic = "force-dynamic";

type ReportsPageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

export default async function ReportsPage({ searchParams = {} }: ReportsPageProps) {
  const filters = parseReportSearchParams(searchParams);
  const summary = await listReports();
  const filteredReports =
    filters.cadence === "all" && filters.platform === "all"
      ? summary.reports
      : summary.reports.filter((report) => {
          const matchesCadence = filters.cadence === "all" || report.cadence === filters.cadence;
          const matchesPlatform = filters.platform === "all" || report.platforms.includes(filters.platform);
          return matchesCadence && matchesPlatform;
        });

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Phase 2 reports</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Schedule recurring research instead of rebuilding it every week.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
            This view keeps report definitions, recurrence, and delivery snapshots server-rendered so the backend can
            take over without changing the structure of the page.
          </p>
          <Link href="/briefs" className="text-sm text-amber-300 underline-offset-4 hover:underline">
            Turn report patterns into a content brief
          </Link>
          <div className="flex flex-wrap gap-2 text-xs uppercase tracking-[0.24em] text-slate-400">
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Scheduled runs</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Email + dashboard</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Pattern summaries</span>
          </div>
        </div>
        <ReportBuilderForm />
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-glow">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Configured reports</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">{filteredReports.length} report(s) visible</h2>
          </div>
          <p className="text-sm text-slate-400">
            Filters: cadence <span className="text-white">{filters.cadence}</span>, platform{" "}
            <span className="text-white">{filters.platform}</span>
          </p>
        </div>
        <div className="mt-5 grid gap-4">
          {filteredReports.map((report) => (
            <article key={report.id} className="rounded-3xl border border-white/10 bg-slate-950/50 p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-500">{report.cadence} cadence</p>
                  <h3 className="text-xl font-semibold text-white">{report.name}</h3>
                  <p className="max-w-2xl text-sm leading-6 text-slate-300">
                    {report.query} • {report.pattern_summary}
                  </p>
                  {report.pattern_deltas && Object.keys(report.pattern_deltas).length > 0 ? (
                    <p className="text-sm text-slate-400">
                      Trend delta:{" "}
                      <span className="text-white">
                        {Object.entries(report.pattern_deltas)
                          .slice(0, 3)
                          .map(([key, value]) => `${key} ${value > 0 ? `+${value}` : value}`)
                          .join(", ")}
                      </span>
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-wrap gap-2">
                  {report.deliveryChannels.map((channel) => (
                    <span key={channel} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                      {channel}
                    </span>
                  ))}
                  <Link
                    href="/briefs"
                    className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs text-amber-100 transition hover:border-amber-300/50"
                  >
                    Brief from trends
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <ReportHistoryTable runs={summary.recent_runs} />
    </div>
  );
}
