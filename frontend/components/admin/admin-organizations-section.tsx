"use client";

import { useEffect, useState } from "react";

type OrganizationRecord = {
  id: string;
  name: string;
  plan: string;
  locations: number;
  members: number;
  status: string;
  renewalDate: string | null;
};

type AdminOrganizationsSectionProps = {
  organizations: OrganizationRecord[];
  pendingOrganizationId: string | null;
  onChangeTier: (organizationId: string, nextTier: string) => void;
};

const tierOptions = [
  "starter",
  "growth",
  "pro",
  "agency",
  "agency growth",
  "multi-location pro",
  "enterprise"
] as const;

export function AdminOrganizationsSection({
  organizations,
  pendingOrganizationId,
  onChangeTier
}: AdminOrganizationsSectionProps): JSX.Element {
  const [selectedTiers, setSelectedTiers] = useState<Record<string, string>>({});

  useEffect(() => {
    setSelectedTiers(
      Object.fromEntries(organizations.map((organization) => [organization.id, organization.plan]))
    );
  }, [organizations]);

  return (
    <section id="organizations" className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Organizations</p>
          <h2 className="text-2xl font-semibold tracking-tight">Tenant Portfolio</h2>
        </div>
        <p className="text-sm text-slate-400">Subscription tier, footprint, and renewal readiness per tenant.</p>
      </div>

      {organizations.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
          No organizations are available yet.
        </div>
      ) : (
        <div className="mt-6 grid gap-4 xl:grid-cols-3">
          {organizations.map((organization) => (
            <article key={organization.id} className="rounded-2xl border border-border/80 bg-background/60 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold text-slate-100">{organization.name}</p>
                  <p className="mt-1 text-sm text-slate-400">{organization.plan}</p>
                </div>
                <span className="rounded-full border border-border px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-300">
                  {organization.status}
                </span>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Locations</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">{organization.locations}</p>
                </div>
                <div className="rounded-xl border border-border bg-card px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Members</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">{organization.members}</p>
                </div>
              </div>

              <div className="mt-4 flex flex-col gap-3">
                <label className="text-xs uppercase tracking-[0.2em] text-slate-400" htmlFor={`tier-${organization.id}`}>
                  Subscription tier
                </label>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <select
                    id={`tier-${organization.id}`}
                    value={selectedTiers[organization.id] ?? organization.plan}
                    onChange={(event) =>
                      setSelectedTiers((current) => ({
                        ...current,
                        [organization.id]: event.target.value
                      }))
                    }
                    className="min-h-11 flex-1 rounded-xl border border-border bg-card px-4 py-2 text-sm text-slate-100 outline-none"
                  >
                    {tierOptions.map((tier) => (
                      <option key={tier} value={tier}>
                        {tier}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() =>
                      onChangeTier(organization.id, selectedTiers[organization.id] ?? organization.plan)
                    }
                    disabled={
                      pendingOrganizationId === organization.id ||
                      (selectedTiers[organization.id] ?? organization.plan) === organization.plan
                    }
                    className="rounded-xl border border-border px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/5 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {pendingOrganizationId === organization.id ? "Saving..." : "Update tier"}
                  </button>
                </div>
              </div>

              <p className="mt-4 text-sm text-slate-400">
                Renewal window: {organization.renewalDate ?? "Not configured"}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
