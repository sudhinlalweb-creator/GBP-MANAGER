type ServiceHealth = {
  name: string;
  status: string;
  detail: string;
  latency: string;
};

type QueueHealth = {
  queueName: string;
  waiting: number;
  running: number;
  failed24h: number;
};

type AdminSystemHealthSectionProps = {
  services: ServiceHealth[];
  queues: QueueHealth[];
};

function statusTone(status: string): string {
  if (status === "Degraded") {
    return "text-amber-300";
  }
  if (status === "Offline") {
    return "text-rose-300";
  }
  return "text-emerald-300";
}

export function AdminSystemHealthSection({
  services,
  queues
}: AdminSystemHealthSectionProps): JSX.Element {
  return (
    <section id="system-health" className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">System Health</p>
          <h2 className="text-2xl font-semibold tracking-tight">Platform Services and Queues</h2>
        </div>
        <p className="text-sm text-slate-400">Core runtime posture for API, workers, data, and monitoring.</p>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-2xl border border-border/80 bg-background/60 p-5">
          <h3 className="text-lg font-semibold text-slate-100">Services</h3>
          {services.length === 0 ? (
            <div className="mt-4 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
              No service telemetry is available yet.
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {services.map((service) => (
                <div
                  key={service.name}
                  className="flex flex-col gap-3 rounded-xl border border-border bg-card px-4 py-4 md:flex-row md:items-center md:justify-between"
                >
                  <div>
                    <p className="font-medium text-slate-100">{service.name}</p>
                    <p className="mt-1 text-sm text-slate-400">{service.detail}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${statusTone(service.status)}`}>{service.status}</p>
                    <p className="mt-1 text-sm text-slate-400">{service.latency}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="rounded-2xl border border-border/80 bg-background/60 p-5">
          <h3 className="text-lg font-semibold text-slate-100">Queues</h3>
          {queues.length === 0 ? (
            <div className="mt-4 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
              No queue telemetry is available yet.
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {queues.map((queue) => (
                <div key={queue.queueName} className="rounded-xl border border-border bg-card px-4 py-4">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-medium text-slate-100">{queue.queueName}</p>
                    <p className="text-sm text-slate-400">{queue.waiting} waiting</p>
                  </div>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Running</p>
                      <p className="mt-1 text-lg font-semibold text-slate-100">{queue.running}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Failed 24h</p>
                      <p className="mt-1 text-lg font-semibold text-slate-100">{queue.failed24h}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
