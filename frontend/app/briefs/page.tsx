import { BriefCard } from "@/components/brief-card";
import { ContentBriefBuilder } from "@/components/content-brief-builder";
import { listBriefs } from "@/lib/briefs";

export const dynamic = "force-dynamic";

type BriefsPageProps = {
  searchParams?: Record<string, string | string[] | undefined>;
};

function parseSelectedIds(value: string | string[] | undefined): number[] {
  const raw = Array.isArray(value) ? value.join(",") : value ?? "";
  return raw
    .split(",")
    .map((entry) => Number(entry.trim()))
    .filter((entry) => Number.isInteger(entry) && entry > 0);
}

export default async function BriefsPage({ searchParams = {} }: BriefsPageProps) {
  const briefs = await listBriefs();
  const selectedIds = parseSelectedIds(searchParams.selectedClipIds);

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Phase 3 briefs</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Turn saved patterns into a brief your team can actually shoot.
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
            Briefs persist the reasoning, selected clips, and recommended shots so pattern research becomes reusable planning output.
          </p>
        </div>
        <ContentBriefBuilder initialSelectedContentDnaIds={selectedIds} />
      </section>

      <section className="space-y-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Saved briefs</p>
          <h2 className="mt-1 text-2xl font-semibold text-white">{briefs.length} brief(s)</h2>
        </div>
        <div className="grid gap-6">
          {briefs.map((brief) => (
            <BriefCard key={brief.briefId} brief={brief} />
          ))}
        </div>
      </section>
    </div>
  );
}
