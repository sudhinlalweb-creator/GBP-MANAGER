type Recommendation = {
  title: string;
  priority: string;
  impact_area: string;
  rationale: string;
};

type AIAuditPanelProps = {
  auditStatus: string;
  recommendationsCount: number;
  lastAuditAt: string;
  openaiEnabled: boolean;
  geminiEnabled: boolean;
  recommendations: Recommendation[];
};

function providerLabel(enabled: boolean): string {
  return enabled ? "Ready" : "Deferred";
}

export function AIAuditPanel(props: AIAuditPanelProps): JSX.Element {
  return (
    <article className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-xl font-semibold">AI Audit Engine</h2>
          <p className="mt-2 text-sm text-slate-300">
            Status: {props.auditStatus} · Last audit: {new Date(props.lastAuditAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-3 text-sm text-slate-300">
          <span className="rounded-full border border-border px-3 py-1">
            OpenAI: {providerLabel(props.openaiEnabled)}
          </span>
          <span className="rounded-full border border-border px-3 py-1">
            Gemini: {providerLabel(props.geminiEnabled)}
          </span>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-border bg-slate-950/50 p-4">
        <p className="text-sm text-slate-400">Recommendations</p>
        <p className="mt-2 text-2xl font-semibold">{props.recommendationsCount}</p>
      </div>

      <div className="mt-6 grid gap-3">
        {props.recommendations.map((recommendation) => (
          <div key={`${recommendation.title}-${recommendation.impact_area}`} className="rounded-2xl border border-border bg-slate-950/50 p-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-base font-medium">{recommendation.title}</h3>
              <span className="rounded-full border border-border px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
                {recommendation.priority}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-400">{recommendation.impact_area}</p>
            <p className="mt-3 text-sm text-slate-300">{recommendation.rationale}</p>
          </div>
        ))}
      </div>
    </article>
  );
}
