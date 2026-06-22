import Link from "next/link";
import type { ReactNode } from "react";

type DashboardShellProps = {
  children: ReactNode;
};

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/dashboard", label: "Operations Dashboard" },
  { href: "/admin", label: "Admin Panel" }
] as const;

export function DashboardShell({ children }: DashboardShellProps): JSX.Element {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto grid min-h-screen max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[240px_1fr]">
        <aside className="rounded-3xl border border-border bg-card p-5">
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">AI Local SEO</p>
          <h1 className="mt-3 text-2xl font-semibold">Operations Console</h1>
          <nav className="mt-8 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block rounded-xl border border-border px-4 py-3 text-sm text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/5"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
        <section className="space-y-6">{children}</section>
      </div>
    </main>
  );
}
