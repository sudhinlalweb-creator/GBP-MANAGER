"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { AIAuditPanel } from "@/components/ai/ai-audit-panel";
import { PhaseThreeScoreCards } from "@/components/ai/phase-three-score-cards";
import { DashboardShell } from "@/components/dashboard-shell";
import { OverviewCards } from "@/components/gbp/overview-cards";
import { ProfileList } from "@/components/gbp/profile-list";
import { IntegrationStatusPanel } from "@/components/integrations/integration-status-panel";
import { KeywordTrendTable } from "@/components/rank-tracking/keyword-trend-table";
import { RecentHeatmapsPanel } from "@/components/rank-tracking/recent-heatmaps-panel";
import { RankTrackingOverviewCards } from "@/components/rank-tracking/track-overview-cards";
import { fetchJson } from "@/lib/api";

type GoogleStatus = {
  organization_id: string;
  organization_name: string;
  organization_role: string;
  google_oauth_configured: boolean;
  google_maps_configured: boolean;
  worker_configured: boolean;
  connected_accounts: number;
  synced_profiles: number;
  last_profile_sync_at: string | null;
};

type GoogleDashboard = {
  organization_id: string;
  organization_name: string;
  connected_accounts: number;
  synced_profiles: number;
  linked_locations: number;
  last_profile_sync_at: string | null;
  profiles: Array<{
    id: string;
    google_location_name: string;
    primary_category: string | null;
    website_url: string | null;
    updated_at: string;
  }>;
};

type AuditSummary = {
  organization_id: string;
  audit_status: string;
  seo_score: number;
  business_health_score: number;
  visibility_score: number;
  profile_completion_score: number;
  last_audit_at: string;
  recommendations_count: number;
  provider_status: {
    openai_enabled: boolean;
    gemini_enabled: boolean;
  };
  recommendations: Array<{
    title: string;
    priority: string;
    impact_area: string;
    rationale: string;
  }>;
};

type RankTrackingOverview = {
  projects_count: number;
  tracked_locations: number;
  active_keywords: number;
  successful_runs_30d: number;
  failed_runs_30d: number;
  average_organic_rank: number | null;
  average_map_pack_rank: number | null;
  visibility_score: number;
  keyword_trends: Array<{
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
  }>;
};

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

const tokenStorageKey = "local-seo-dev-token";

export function PhaseTwoDashboard(): JSX.Element {
  const [tokenInput, setTokenInput] = useState("");
  const [token, setToken] = useState("");

  useEffect(() => {
    const storedToken = window.localStorage.getItem(tokenStorageKey) ?? "";
    setToken(storedToken);
    setTokenInput(storedToken);
  }, []);

  const statusQuery = useQuery({
    queryKey: ["google-status", token],
    queryFn: () => fetchJson<GoogleStatus>("/google/status", token),
    enabled: token.length > 0
  });

  const dashboardQuery = useQuery({
    queryKey: ["google-dashboard", token],
    queryFn: () => fetchJson<GoogleDashboard>("/dashboard/gbp", token),
    enabled: token.length > 0
  });

  const auditSummaryQuery = useQuery({
    queryKey: ["audit-summary", token],
    queryFn: () => fetchJson<AuditSummary>("/audit/summary", token),
    enabled: token.length > 0
  });

  const rankOverviewQuery = useQuery({
    queryKey: ["rank-tracking-overview", token],
    queryFn: () => fetchJson<RankTrackingOverview>("/track/overview", token),
    enabled: token.length > 0
  });

  const heatmapsQuery = useQuery({
    queryKey: ["heatmaps-recent", token],
    queryFn: () => fetchJson<HeatmapRun[]>("/track/heatmaps/recent", token),
    enabled: token.length > 0
  });

  const handleSaveToken = (): void => {
    window.localStorage.setItem(tokenStorageKey, tokenInput.trim());
    setToken(tokenInput.trim());
  };

  const errorMessage =
    (statusQuery.error as Error | undefined)?.message ??
    (dashboardQuery.error as Error | undefined)?.message ??
    (auditSummaryQuery.error as Error | undefined)?.message ??
    (rankOverviewQuery.error as Error | undefined)?.message ??
    (heatmapsQuery.error as Error | undefined)?.message ??
    null;

  const isLoading =
    statusQuery.isLoading ||
    dashboardQuery.isLoading ||
    auditSummaryQuery.isLoading ||
    rankOverviewQuery.isLoading ||
    heatmapsQuery.isLoading;

  const hasData =
    statusQuery.data &&
    dashboardQuery.data &&
    auditSummaryQuery.data &&
    rankOverviewQuery.data &&
    heatmapsQuery.data;

  return (
    <DashboardShell>
      <header className="rounded-3xl border border-border bg-card p-8">
        <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Phase 2-4</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Local SEO Operations Dashboard</h1>
        <p className="mt-4 max-w-3xl text-slate-300">
          Use a bearer token from the backend auth API to inspect Google integration readiness, AI audit signals,
          keyword tracking, and the new persisted heatmap foundations while the full frontend auth flow is still under
          construction.
        </p>
      </header>

      <section className="rounded-3xl border border-border bg-card p-6">
        <label className="block text-sm font-medium text-slate-300" htmlFor="dev-token">
          Developer bearer token
        </label>
        <div className="mt-3 flex flex-col gap-3 lg:flex-row">
          <input
            id="dev-token"
            value={tokenInput}
            onChange={(event) => setTokenInput(event.target.value)}
            placeholder="Paste access_token from /api/v1/auth/login"
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
      </section>

      {!token ? null : isLoading ? (
        <section className="rounded-3xl border border-border bg-card p-6 text-slate-300">
          Loading dashboard data...
        </section>
      ) : hasData ? (
        <>
          <OverviewCards
            connectedAccounts={dashboardQuery.data.connected_accounts}
            syncedProfiles={dashboardQuery.data.synced_profiles}
            linkedLocations={dashboardQuery.data.linked_locations}
            lastProfileSyncAt={dashboardQuery.data.last_profile_sync_at}
          />
          <IntegrationStatusPanel
            organizationName={statusQuery.data.organization_name}
            organizationRole={statusQuery.data.organization_role}
            googleOauthConfigured={statusQuery.data.google_oauth_configured}
            googleMapsConfigured={statusQuery.data.google_maps_configured}
            workerConfigured={statusQuery.data.worker_configured}
            connectedAccounts={statusQuery.data.connected_accounts}
            syncedProfiles={statusQuery.data.synced_profiles}
            lastProfileSyncAt={statusQuery.data.last_profile_sync_at}
          />
          <PhaseThreeScoreCards
            seoScore={auditSummaryQuery.data.seo_score}
            businessHealthScore={auditSummaryQuery.data.business_health_score}
            visibilityScore={auditSummaryQuery.data.visibility_score}
            profileCompletionScore={auditSummaryQuery.data.profile_completion_score}
          />
          <AIAuditPanel
            auditStatus={auditSummaryQuery.data.audit_status}
            recommendationsCount={auditSummaryQuery.data.recommendations_count}
            lastAuditAt={auditSummaryQuery.data.last_audit_at}
            openaiEnabled={auditSummaryQuery.data.provider_status.openai_enabled}
            geminiEnabled={auditSummaryQuery.data.provider_status.gemini_enabled}
            recommendations={auditSummaryQuery.data.recommendations}
          />
          <RankTrackingOverviewCards
            projectsCount={rankOverviewQuery.data.projects_count}
            trackedLocations={rankOverviewQuery.data.tracked_locations}
            activeKeywords={rankOverviewQuery.data.active_keywords}
            successfulRuns30d={rankOverviewQuery.data.successful_runs_30d}
            failedRuns30d={rankOverviewQuery.data.failed_runs_30d}
            averageOrganicRank={rankOverviewQuery.data.average_organic_rank}
            averageMapPackRank={rankOverviewQuery.data.average_map_pack_rank}
            visibilityScore={rankOverviewQuery.data.visibility_score}
          />
          <KeywordTrendTable trends={rankOverviewQuery.data.keyword_trends} />
          <RecentHeatmapsPanel heatmaps={heatmapsQuery.data} />
          <ProfileList profiles={dashboardQuery.data.profiles} />
        </>
      ) : null}
    </DashboardShell>
  );
}
