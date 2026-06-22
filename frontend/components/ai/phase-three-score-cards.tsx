type PhaseThreeScoreCardsProps = {
  seoScore: number;
  businessHealthScore: number;
  visibilityScore: number;
  profileCompletionScore: number;
};

export function PhaseThreeScoreCards(props: PhaseThreeScoreCardsProps): JSX.Element {
  const cards = [
    { label: "SEO Score", value: String(props.seoScore) },
    { label: "Business Health", value: String(props.businessHealthScore) },
    { label: "Visibility Score", value: String(props.visibilityScore) },
    { label: "Profile Completion", value: String(props.profileCompletionScore) }
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article key={card.label} className="rounded-2xl border border-border bg-card p-5">
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="mt-3 text-3xl font-semibold">{card.value}</p>
        </article>
      ))}
    </section>
  );
}
