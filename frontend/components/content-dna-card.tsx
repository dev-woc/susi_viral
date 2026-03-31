import type { ContentDNA } from "@/lib/types";

interface ContentDnaCardProps {
  contentDna: ContentDNA;
}

function TagList({ tags }: { tags: string[] }) {
  if (tags.length === 0) {
    return <p className="text-sm text-slate-500">No pattern tags extracted yet.</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <span key={tag} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
          {tag}
        </span>
      ))}
    </div>
  );
}

export function ContentDnaCard({ contentDna }: ContentDnaCardProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/50 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">ContentDNA</p>
          <h3 className="mt-1 text-xl font-semibold text-white">{contentDna.hook ?? "Hook unavailable"}</h3>
        </div>
        <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">
          {contentDna.virality_score}
        </div>
      </div>
      <dl className="mt-5 grid gap-4 sm:grid-cols-2">
        <Detail label="Platform" value={contentDna.platform.replace("_", " ")} />
        <Detail label="Format" value={contentDna.format ?? "Not captured"} />
        <Detail label="Emotion" value={contentDna.emotion ?? "Not captured"} />
        <Detail label="CTA" value={contentDna.cta ?? "Not captured"} />
      </dl>
      <div className="mt-5 space-y-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Structure</p>
          <p className="mt-2 text-sm leading-6 text-slate-300">{contentDna.structure ?? "No structure summary available."}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Replication notes</p>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            {contentDna.replication_notes ?? "No replication note captured yet."}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Pattern tags</p>
          <div className="mt-2">
            <TagList tags={contentDna.pattern_tags} />
          </div>
        </div>
      </div>
    </section>
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
