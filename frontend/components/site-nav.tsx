import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/search", label: "Search" },
  { href: "/library", label: "Library" },
  { href: "/reports", label: "Reports" },
  { href: "/briefs", label: "Briefs" },
  { href: "/workspaces", label: "Workspaces" },
];

export function SiteNav() {
  return (
    <header className="border-b border-white/10 bg-black/10 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="group flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-amber-300 shadow-glow">
            VC
          </span>
          <span>
            <span className="block text-sm uppercase tracking-[0.32em] text-slate-400">Viral Content Agent</span>
            <span className="block text-lg font-semibold text-white">Search, extract, save</span>
          </span>
        </Link>
        <nav className="flex items-center gap-2">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:border-amber-400/40 hover:bg-white/5 hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
