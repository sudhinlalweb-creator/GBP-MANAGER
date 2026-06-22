type HeatmapRun = {
  id: string;
  project_id: string;
  target_location_id: string;
  keyword_id: string | null;
  project_name: string | null;
  location_label: string | null;
  keyword_phrase: string | null;
  status: string;
  error_reason: string | null;
  grid_size: number;
  radius_meters: number;
  grid_points_total: number;
  center_latitude: number;
  center_longitude: number;
  points: Array<{
    latitude: number;
    longitude: number;
    organic_rank: number | null;
    map_pack_rank: number | null;
    grid_row: number;
    grid_col: number;
  }>;
  summary: {
    grid_points_completed?: number;
    best_organic_rank?: number | null;
    best_map_pack_rank?: number | null;
    average_organic_rank?: number | null;
    average_map_pack_rank?: number | null;
  } | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

type RecentHeatmapsPanelProps = {
  heatmaps: HeatmapRun[];
};

function formatDate(value: string | null): string {
  return value ? new Date(value).toLocaleString() : "In progress";
}

function formatBestRank(value: number | null | undefined): string {
  return value ? `#${value}` : "-";
}

export function RecentHeatmapsPanel({ heatmaps }: RecentHeatmapsPanelProps): JSX.Element {
  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Geo Grid</p>
          <h2 className="text-2xl font-semibold tracking-tight">Recent Heatmap Runs</h2>
        </div>
        <p className="text-sm text-slate-400">Persisted 5x5, 7x7, and 9x9 grid outputs land here.</p>
      </div>

      {heatmaps.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
          No heatmap runs exist yet. Use the protected
          {" "}<code>/api/v1/track/projects/{"{project_id}"}/heatmaps</code>{" "}
          endpoint to queue the first one.
        </div>
      ) : (
        <div className="mt-6 grid gap-4 xl:grid-cols-2">
          {heatmaps.map((heatmap) => (
            <article key={heatmap.id} className="rounded-2xl border border-border/80 bg-background/60 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-base font-semibold text-slate-100">
                    {heatmap.keyword_phrase ?? "Project heatmap"}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">
                    {heatmap.project_name ?? "Unknown project"} • {heatmap.location_label ?? "Unknown location"}
                  </p>
                </div>
                <span className="rounded-full border border-border px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-300">
                  {heatmap.status}
                </span>
              </div>

              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Grid</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">
                    {heatmap.grid_size}x{heatmap.grid_size}
                  </p>
                  <p className="text-sm text-slate-400">{heatmap.grid_points_total} points</p>
                </div>
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Radius</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">{heatmap.radius_meters} m</p>
                  <p className="text-sm text-slate-400">Completed {heatmap.summary?.grid_points_completed ?? 0}</p>
                </div>
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Best Organic</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">
                    {formatBestRank(heatmap.summary?.best_organic_rank)}
                  </p>
                </div>
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Best Map Pack</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">
                    {formatBestRank(heatmap.summary?.best_map_pack_rank)}
                  </p>
                </div>
              </div>

              <div className="mt-4 space-y-1 text-sm text-slate-400">
                <p>Completed: {formatDate(heatmap.completed_at)}</p>
                {heatmap.error_reason ? <p className="text-rose-300">Error: {heatmap.error_reason}</p> : null}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
