"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { AdminOrganizationsSection } from "@/components/admin/admin-organizations-section";
import { AdminOverviewCards } from "@/components/admin/admin-overview-cards";
import { AdminSubscriptionsSection } from "@/components/admin/admin-subscriptions-section";
import { AdminSystemHealthSection } from "@/components/admin/admin-system-health-section";
import { AdminUsersSection } from "@/components/admin/admin-users-section";
import { DashboardShell } from "@/components/dashboard-shell";
import { fetchJson, patchJson } from "@/lib/api";

type AdminDashboardResponse = {
  overview: {
    active_users: number;
    organizations: number;
    monthly_recurring_revenue: number;
    incident_status: string;
  };
  users: Array<{
    id: string;
    name: string | null;
    email: string;
    role: string;
    organization: string | null;
    status: string;
    is_active: boolean;
    last_active_at: string;
  }>;
  organizations: Array<{
    id: string;
    name: string;
    subscription_tier: string;
    locations_count: number;
    members_count: number;
    status: string;
    renewal_date: string | null;
  }>;
  subscriptions: Array<{
    tier: string;
    tenants_count: number;
    members_count: number;
    estimated_monthly_revenue: number;
    status: string;
  }>;
  system_health: {
    services: Array<{
      name: string;
      status: string;
      detail: string;
      metric: string;
    }>;
    queues: Array<{
      queue_name: string;
      waiting: number;
      running: number;
      failed_24h: number;
    }>;
  };
};

const tokenStorageKey = "local-seo-dev-token";

const anchorLinks = [
  { href: "#users", label: "Users" },
  { href: "#organizations", label: "Organizations" },
  { href: "#subscriptions", label: "Subscriptions" },
  { href: "#system-health", label: "System Health" }
] as const;

export function AdminPanel(): JSX.Element {
  const queryClient = useQueryClient();
  const [tokenInput, setTokenInput] = useState("");
  const [token, setToken] = useState("");

  useEffect(() => {
    const storedToken = window.localStorage.getItem(tokenStorageKey) ?? "";
    setToken(storedToken);
    setTokenInput(storedToken);
  }, []);

  const adminQuery = useQuery({
    queryKey: ["admin-summary", token],
    queryFn: () => fetchJson<AdminDashboardResponse>("/admin/summary", token),
    enabled: token.length > 0
  });

  const userStatusMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      patchJson<
        AdminDashboardResponse["users"][number],
        { is_active: boolean }
      >(`/admin/users/${userId}`, token, { is_active: isActive }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-summary", token] });
    }
  });

  const organizationTierMutation = useMutation({
    mutationFn: ({ organizationId, tier }: { organizationId: string; tier: string }) =>
      patchJson<
        AdminDashboardResponse["organizations"][number],
        { subscription_tier: string }
      >(`/admin/organizations/${organizationId}`, token, { subscription_tier: tier }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-summary", token] });
    }
  });

  const handleSaveToken = (): void => {
    window.localStorage.setItem(tokenStorageKey, tokenInput.trim());
    setToken(tokenInput.trim());
  };

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0
    }).format(value);

  const errorMessage =
    (adminQuery.error as Error | undefined)?.message ??
    (userStatusMutation.error as Error | undefined)?.message ??
    (organizationTierMutation.error as Error | undefined)?.message ??
    null;

  const handleToggleUserStatus = (userId: string, nextIsActive: boolean): void => {
    userStatusMutation.mutate({ userId, isActive: nextIsActive });
  };

  const handleChangeOrganizationTier = (organizationId: string, nextTier: string): void => {
    organizationTierMutation.mutate({ organizationId, tier: nextTier });
  };

  return (
    <DashboardShell>
      <header className="rounded-3xl border border-border bg-card p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Admin Control Center</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight">SaaS Admin Panel</h1>
            <p className="mt-4 max-w-3xl text-slate-300">
              Central workspace for platform operators to monitor tenant access, revenue posture, and system health.
              This shell is ready to be connected to real admin APIs next.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {anchorLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="rounded-2xl border border-border bg-background/60 px-4 py-3 text-sm text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/5"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </header>

      <section className="rounded-3xl border border-border bg-card p-6">
        <label className="block text-sm font-medium text-slate-300" htmlFor="admin-token">
          Admin bearer token
        </label>
        <div className="mt-3 flex flex-col gap-3 lg:flex-row">
          <input
            id="admin-token"
            value={tokenInput}
            onChange={(event) => setTokenInput(event.target.value)}
            placeholder="Paste superuser access_token from /api/v1/auth/login"
            className="min-h-12 flex-1 rounded-2xl border border-border bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none"
          />
          <button
            type="button"
            onClick={handleSaveToken}
            className="rounded-2xl bg-emerald-500 px-5 py-3 text-sm font-medium text-slate-950 transition hover:bg-emerald-400"
          >
            Save token
          </button>
        </div>
        {errorMessage ? <p className="mt-3 text-sm text-rose-300">{errorMessage}</p> : null}
        {!token ? (
          <p className="mt-3 text-sm text-slate-400">
            The first registered user is promoted to superuser automatically for local bootstrap access.
          </p>
        ) : null}
      </section>

      {!token ? null : adminQuery.isLoading ? (
        <section className="rounded-3xl border border-border bg-card p-6 text-slate-300">
          Loading admin control center...
        </section>
      ) : adminQuery.data ? (
        <>
          <AdminOverviewCards
            usersCount={adminQuery.data.overview.active_users}
            organizationsCount={adminQuery.data.overview.organizations}
            mrr={formatCurrency(adminQuery.data.overview.monthly_recurring_revenue)}
            incidentStatus={adminQuery.data.overview.incident_status}
          />
          <AdminUsersSection
            users={adminQuery.data.users.map((user) => ({
              id: user.id,
              name: user.name ?? "Unnamed user",
              email: user.email,
              role: user.role,
              organization: user.organization ?? "No organization",
              status: user.status,
              isActive: user.is_active,
              lastActive: new Date(user.last_active_at).toLocaleString()
            }))}
            pendingUserId={userStatusMutation.isPending ? userStatusMutation.variables?.userId ?? null : null}
            onToggleUserStatus={handleToggleUserStatus}
          />
          <AdminOrganizationsSection
            organizations={adminQuery.data.organizations.map((organization) => ({
              id: organization.id,
              name: organization.name,
              plan: organization.subscription_tier,
              locations: organization.locations_count,
              members: organization.members_count,
              status: organization.status,
              renewalDate: organization.renewal_date
                ? new Date(organization.renewal_date).toLocaleDateString()
                : null
            }))}
            pendingOrganizationId={
              organizationTierMutation.isPending
                ? organizationTierMutation.variables?.organizationId ?? null
                : null
            }
            onChangeTier={handleChangeOrganizationTier}
          />
          <AdminSubscriptionsSection
            subscriptions={adminQuery.data.subscriptions.map((subscription) => ({
              id: subscription.tier,
              planName: subscription.tier,
              tenants: subscription.tenants_count,
              seats: `${subscription.members_count} members`,
              mrr: formatCurrency(subscription.estimated_monthly_revenue),
              churnRisk: subscription.status
            }))}
          />
          <AdminSystemHealthSection
            services={adminQuery.data.system_health.services.map((service) => ({
              name: service.name,
              status: service.status,
              detail: service.detail,
              latency: service.metric
            }))}
            queues={adminQuery.data.system_health.queues.map((queue) => ({
              queueName: queue.queue_name,
              waiting: queue.waiting,
              running: queue.running,
              failed24h: queue.failed_24h
            }))}
          />
        </>
      ) : null}
    </DashboardShell>
  );
}
