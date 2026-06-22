type KeywordTrend = {
  keyword_id: string;
  project_id: string;
  phrase: string;
  latest_organic_rank: number | null;
  previous_organic_rank: number | null;
  latest_map_pack_rank: number | null;
  trend_direction: string;
  successful_runs: number;
  failed_runs: number;
  last_captured_at: string | null;
};

type KeywordTrendTableProps = {
  trends: KeywordTrend[];
};

function formatRank(rank: number | null): string {
  return rank === null ? "-" : `#${rank}`;
}

function formatTrendLabel(direction: string): string {
  if (direction === "up") {
    return "Improving";
  }
  if (direction === "down") {
    return "Dropping";
  }
  return "Stable";
}

function formatCapturedAt(value: string | null): string {
  return value ? new Date(value).toLocaleString() : "Not captured yet";
}

export function KeywordTrendTable({ trends }: KeywordTrendTableProps): JSX.Element {
  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Phase 4</p>
          <h2 className="text-2xl font-semibold tracking-tight">Keyword Tracking Trends</h2>
        </div>
        <p className="text-sm text-slate-400">Recent organic and map pack movement across tracked terms.</p>
      </div>

      {trends.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
          No keyword history is available yet. Queue rank tracking runs from the API to populate this table.
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-sm">
            <thead>
              <tr className="text-left text-slate-400">
                <th className="pb-3 pr-4 font-medium">Keyword</th>
                <th className="pb-3 pr-4 font-medium">Organic</th>
                <th className="pb-3 pr-4 font-medium">Previous</th>
                <th className="pb-3 pr-4 font-medium">Map Pack</th>
                <th className="pb-3 pr-4 font-medium">Trend</th>
                <th className="pb-3 pr-4 font-medium">Runs</th>
                <th className="pb-3 font-medium">Last Captured</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/80">
              {trends.map((trend) => (
                <tr key={trend.keyword_id}>
                  <td className="py-4 pr-4">
                    <p className="font-medium text-slate-100">{trend.phrase}</p>
                  </td>
                  <td className="py-4 pr-4 text-slate-200">{formatRank(trend.latest_organic_rank)}</td>
                  <td className="py-4 pr-4 text-slate-400">{formatRank(trend.previous_organic_rank)}</td>
                  <td className="py-4 pr-4 text-slate-200">{formatRank(trend.latest_map_pack_rank)}</td>
                  <td className="py-4 pr-4 text-slate-200">{formatTrendLabel(trend.trend_direction)}</td>
                  <td className="py-4 pr-4 text-slate-400">
                    {trend.successful_runs} ok / {trend.failed_runs} failed
                  </td>
                  <td className="py-4 text-slate-400">{formatCapturedAt(trend.last_captured_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
