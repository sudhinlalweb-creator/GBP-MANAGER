type RankTrackingOverviewCardsProps = {
  projectsCount: number;
  trackedLocations: number;
  activeKeywords: number;
  successfulRuns30d: number;
  failedRuns30d: number;
  averageOrganicRank: number | null;
  averageMapPackRank: number | null;
  visibilityScore: number;
};

function formatMetric(value: number | null): string {
  if (value === null) {
    return "No data yet";
  }

  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export function RankTrackingOverviewCards(
  props: RankTrackingOverviewCardsProps
): JSX.Element {
  const cards = [
    { label: "Tracked Projects", value: String(props.projectsCount) },
    { label: "Tracked Locations", value: String(props.trackedLocations) },
    { label: "Active Keywords", value: String(props.activeKeywords) },
    { label: "Successful Runs (30d)", value: String(props.successfulRuns30d) },
    { label: "Failed Runs (30d)", value: String(props.failedRuns30d) },
    { label: "Average Organic Rank", value: formatMetric(props.averageOrganicRank) },
    { label: "Average Map Pack Rank", value: formatMetric(props.averageMapPackRank) },
    { label: "Visibility Score", value: formatMetric(props.visibilityScore) }
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article key={card.label} className="rounded-2xl border border-border bg-card p-5">
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="mt-3 text-2xl font-semibold">{card.value}</p>
        </article>
      ))}
    </section>
  );
}
