type OverviewCardsProps = {
  connectedAccounts: number;
  syncedProfiles: number;
  linkedLocations: number;
  lastProfileSyncAt: string | null;
};

export function OverviewCards(props: OverviewCardsProps): JSX.Element {
  const cards = [
    { label: "Connected Accounts", value: String(props.connectedAccounts) },
    { label: "Synced Profiles", value: String(props.syncedProfiles) },
    { label: "Linked Locations", value: String(props.linkedLocations) },
    {
      label: "Last Sync",
      value: props.lastProfileSyncAt
        ? new Date(props.lastProfileSyncAt).toLocaleString()
        : "Not synced yet"
    }
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
