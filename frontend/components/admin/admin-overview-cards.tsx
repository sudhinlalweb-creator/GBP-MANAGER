type AdminOverviewCardsProps = {
  usersCount: number;
  organizationsCount: number;
  mrr: string;
  incidentStatus: string;
};

export function AdminOverviewCards(props: AdminOverviewCardsProps): JSX.Element {
  const cards = [
    { label: "Active Users", value: String(props.usersCount), detail: "Authenticated seats across all tenants" },
    {
      label: "Organizations",
      value: String(props.organizationsCount),
      detail: "Agency and single-location tenants"
    },
    { label: "Monthly Recurring Revenue", value: props.mrr, detail: "Projected subscription revenue" },
    { label: "Incident Status", value: props.incidentStatus, detail: "Current platform severity window" }
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article key={card.label} className="rounded-2xl border border-border bg-card p-5">
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="mt-3 text-2xl font-semibold text-slate-100">{card.value}</p>
          <p className="mt-2 text-sm text-slate-300">{card.detail}</p>
        </article>
      ))}
    </section>
  );
}
