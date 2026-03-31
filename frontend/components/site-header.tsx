import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b border-white/10 bg-ink/55 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.35em] text-sand/70">
            Viral Content Agent
          </p>
          <Link href="/" className="text-lg font-semibold tracking-tight text-paper">
            Phase 1 MVP
          </Link>
        </div>
        <nav className="flex items-center gap-2 text-sm">
          <Link
            href="/search"
            className="rounded-full border border-white/10 px-4 py-2 text-paper/90 transition hover:border-sand/40 hover:bg-white/5"
          >
            Search
          </Link>
          <Link
            href="/library"
            className="rounded-full bg-moss px-4 py-2 font-medium text-paper transition hover:bg-moss/90"
          >
            Library
          </Link>
        </nav>
      </div>
    </header>
  );
}
