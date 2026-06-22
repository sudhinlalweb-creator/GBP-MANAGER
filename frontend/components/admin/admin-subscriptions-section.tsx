type SubscriptionRecord = {
  id: string;
  planName: string;
  tenants: number;
  seats: string;
  mrr: string;
  churnRisk: string;
};

type AdminSubscriptionsSectionProps = {
  subscriptions: SubscriptionRecord[];
};

export function AdminSubscriptionsSection({
  subscriptions
}: AdminSubscriptionsSectionProps): JSX.Element {
  return (
    <section id="subscriptions" className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Subscriptions</p>
          <h2 className="text-2xl font-semibold tracking-tight">Revenue and Plan Mix</h2>
        </div>
        <p className="text-sm text-slate-400">Current plan distribution and expansion risk indicators.</p>
      </div>

      {subscriptions.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
          No subscription data is available yet.
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-sm">
            <thead>
              <tr className="text-left text-slate-400">
                <th className="pb-3 pr-4 font-medium">Plan</th>
                <th className="pb-3 pr-4 font-medium">Tenants</th>
                <th className="pb-3 pr-4 font-medium">Seat Utilization</th>
                <th className="pb-3 pr-4 font-medium">MRR</th>
                <th className="pb-3 font-medium">Churn Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/80">
              {subscriptions.map((subscription) => (
                <tr key={subscription.id}>
                  <td className="py-4 pr-4 font-medium text-slate-100">{subscription.planName}</td>
                  <td className="py-4 pr-4 text-slate-300">{subscription.tenants}</td>
                  <td className="py-4 pr-4 text-slate-300">{subscription.seats}</td>
                  <td className="py-4 pr-4 text-slate-200">{subscription.mrr}</td>
                  <td className="py-4 text-slate-400">{subscription.churnRisk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
