import { ContentDnaCard } from "@/components/content-dna-card";
import type { ContentBrief } from "@/lib/briefs";

export function BriefCard({ brief }: { brief: ContentBrief }) {
  return (
    <article className="space-y-5 rounded-[2rem] border border-white/10 bg-slate-950/55 p-6 shadow-glow">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Brief {brief.briefId}</p>
          <h3 className="text-2xl font-semibold text-white">{brief.title}</h3>
          <p className="max-w-3xl text-sm leading-6 text-slate-300">{brief.summary}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
          {new Date(brief.createdAt).toLocaleString()}
        </div>
      </div>
      <dl className="grid gap-4 md:grid-cols-3">
        <Detail label="Objective" value={brief.objective} />
        <Detail label="Audience" value={brief.audience} />
        <Detail label="Tone" value={brief.tone ?? "Not specified"} />
      </dl>
      <div className="grid gap-5 lg:grid-cols-[0.7fr_1.3fr]">
        <section className="rounded-3xl border border-white/10 bg-white/5 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Recommended shots</p>
          <ul className="mt-3 space-y-3 text-sm leading-6 text-slate-200">
            {brief.recommendedShots.map((shot) => (
              <li key={shot} className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
                {shot}
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap gap-2">
            {brief.patternTags.map((tag) => (
              <span key={tag} className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs text-amber-100">
                {tag}
              </span>
            ))}
          </div>
        </section>
        <section className="space-y-4">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Selected clips</p>
          <div className="grid gap-4">
            {brief.selectedClips.map((clip) => (
              <ContentDnaCard key={`${brief.briefId}-${clip.id ?? clip.clip_id}`} contentDna={clip} />
            ))}
          </div>
        </section>
      </div>
    </article>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <dt className="text-xs uppercase tracking-[0.24em] text-slate-500">{label}</dt>
      <dd className="mt-2 text-sm text-slate-100">{value}</dd>
    </div>
  );
}
