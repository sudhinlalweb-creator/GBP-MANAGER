type StatCard = {
  label: string;
  value: string;
  detail: string;
};

const stats: StatCard[] = [
  { label: "Organizations", value: "128", detail: "Agency and SMB tenants" },
  { label: "Tracked Profiles", value: "2,940", detail: "Connected Google Business Profiles" },
  { label: "Keywords", value: "84,200", detail: "Local SERP terms monitored" },
  { label: "Automations", value: "415", detail: "Scheduled audits, reports, and alerts" }
];

const modules = [
  "Google Business Profile Sync",
  "AI Business Audit",
  "Local Rank Tracking",
  "Maps Grid Heatmaps",
  "Competitor Intelligence",
  "Review Management",
  "Google Posts",
  "Reports and White Labeling"
];

export function AppShell(): JSX.Element {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="mx-auto flex max-w-7xl flex-col gap-10 px-6 py-12">
        <header className="rounded-3xl border border-border bg-card p-8 shadow-2xl shadow-black/20">
          <p className="mb-3 inline-flex rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
            AI-first Local SEO SaaS
          </p>
          <h1 className="max-w-4xl text-4xl font-semibold tracking-tight sm:text-5xl">
            Operating system for Google Business Profile optimization, local rank intelligence, and agency automation.
          </h1>
          <p className="mt-4 max-w-3xl text-lg text-slate-300">
            This workspace is re-baselined for a production-ready multi-tenant SaaS with a Next.js frontend,
            FastAPI backend, Celery workers, and pluggable AI + Google integrations.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {stats.map((stat) => (
            <article key={stat.label} className="rounded-2xl border border-border bg-card p-6">
              <p className="text-sm text-slate-400">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold">{stat.value}</p>
              <p className="mt-2 text-sm text-slate-300">{stat.detail}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          <article className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Platform Modules</h2>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {modules.map((module) => (
                <div key={module} className="rounded-xl border border-border bg-slate-950/60 px-4 py-3 text-sm text-slate-200">
                  {module}
                </div>
              ))}
            </div>
          </article>

          <article className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Delivery Milestones</h2>
            <ol className="mt-5 space-y-4 text-sm text-slate-300">
              <li>1. SaaS foundation: auth, organizations, billing, deployment</li>
              <li>2. Google Business Profile sync and dashboard analytics</li>
              <li>3. AI audit engine and health scoring</li>
              <li>4. Keyword tracking, rank history, and heatmaps</li>
              <li>5. Reviews, posts, reports, and agency workflows</li>
            </ol>
          </article>
        </section>
      </section>
    </main>
  );
}
