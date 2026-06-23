"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import { ScoreRing } from "@/components/ui/score-ring"
import type { GoogleBusinessProfile } from "@/lib/types"

function StatCard({ label, value, sub, icon }: { label: string; value: string | number; sub?: string; icon: JSX.Element }) {
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 14, padding: "20px 22px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <p style={{ fontSize: 13, color: "var(--ink-muted)", fontWeight: 500 }}>{label}</p>
        <span style={{ width: 34, height: 34, borderRadius: 9, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--fin)", flexShrink: 0 }}>{icon}</span>
      </div>
      <div>
        <p style={{ fontSize: 28, fontWeight: 600, color: "var(--ink)", letterSpacing: "-0.5px", lineHeight: 1 }}>{value}</p>
        {sub && <p style={{ fontSize: 12, color: "var(--ink-tertiary)", marginTop: 4 }}>{sub}</p>}
      </div>
    </div>
  )
}

export default function DashboardPage(): JSX.Element {
  const { activeOrgId, user } = useAuth()
  const firstName = user?.full_name?.split(" ")[0] ?? "there"

  const { data: profiles, isLoading } = useQuery<GoogleBusinessProfile[]>({
    queryKey: ["profiles", activeOrgId],
    queryFn: () =>
      api.get<{ profiles: GoogleBusinessProfile[] } | GoogleBusinessProfile[]>("/google/profiles").then(
        (r) => (Array.isArray(r) ? r : r.profiles),
      ),
    enabled: !!activeOrgId,
  })

  const connected = profiles?.filter((p) => !p.is_disconnected).length ?? 0
  const avgScore =
    profiles && profiles.length > 0
      ? Math.round(profiles.reduce((s, p) => s + (p.completeness_score ?? 0), 0) / profiles.length)
      : null
  const totalReviews = profiles?.reduce((s, p) => s + (p.review_count ?? 0), 0) ?? 0
  const avgRating =
    profiles && profiles.length
      ? (profiles.reduce((s, p) => s + (p.average_rating ?? 0), 0) / profiles.length).toFixed(1)
      : null

  return (
    <div style={{ maxWidth: 900 }}>
      {/* Greeting */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 600, color: "var(--ink)", letterSpacing: "-0.3px" }}>Good morning, {firstName} 👋</h1>
        <p style={{ fontSize: 14, color: "var(--ink-muted)", marginTop: 3 }}>Here&apos;s an overview of your Google Business Profiles.</p>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 28 }}>
        <StatCard
          label="Connected Profiles"
          value={connected}
          sub={profiles?.length ? `${profiles.length} total` : undefined}
          icon={<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>}
        />
        <StatCard
          label="Avg Completeness"
          value={avgScore != null ? `${avgScore}%` : "—"}
          sub="profile health"
          icon={<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><rect x="7" y="11" width="3" height="6" rx="1"/><rect x="12" y="7" width="3" height="10" rx="1"/><rect x="17" y="13" width="3" height="4" rx="1"/></svg>}
        />
        <StatCard
          label="Total Reviews"
          value={totalReviews}
          sub="across all profiles"
          icon={<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M11.5 3.5 14 8.6l5.6.8-4 4 1 5.6-5.1-2.7L6.4 19l1-5.6-4-4 5.6-.8z"/></svg>}
        />
        <StatCard
          label="Avg Rating"
          value={avgRating ?? "—"}
          sub="out of 5.0 stars"
          icon={<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>}
        />
      </div>

      {/* Profiles list */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, color: "var(--ink)" }}>Business Profiles</h2>
          <Link href="/profiles" style={{ fontSize: 13, color: "var(--fin)", textDecoration: "none", fontWeight: 500 }}>View all →</Link>
        </div>

        {isLoading && (
          <div style={{ display: "flex", justifyContent: "center", padding: "40px 0" }}>
            <Spinner />
          </div>
        )}

        {!isLoading && (!profiles || profiles.length === 0) && (
          <div style={{ background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 14, padding: "48px 40px", textAlign: "center" }}>
            <div style={{ width: 56, height: 56, borderRadius: 14, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 18px" }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>
            </div>
            <h3 style={{ fontSize: 16, fontWeight: 600, color: "var(--ink)", marginBottom: 6 }}>No profiles connected</h3>
            <p style={{ fontSize: 14, color: "var(--ink-muted)", marginBottom: 22, maxWidth: 340, margin: "0 auto 22px" }}>Connect your Google Business account to start managing your locations from one place.</p>
            <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
              <Link href="/profiles" style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "var(--btn-bg)", color: "var(--btn-fg)", borderRadius: 9, padding: "9px 18px", fontSize: 13.5, fontWeight: 500, textDecoration: "none" }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14"/></svg>
                Connect Google Account
              </Link>
              <a href="https://support.google.com/business" target="_blank" rel="noopener noreferrer" style={{ display: "inline-flex", alignItems: "center", background: "var(--surface-2)", color: "var(--ink-muted)", border: "1px solid var(--hairline)", borderRadius: 9, padding: "9px 18px", fontSize: 13.5, textDecoration: "none" }}>
                Learn more
              </a>
            </div>
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {profiles?.slice(0, 6).map((profile) => (
            <Link
              key={profile.id}
              href={`/profiles/${profile.id}`}
              style={{ display: "flex", alignItems: "center", gap: 16, background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 12, padding: "14px 18px", textDecoration: "none", transition: "border-color .15s" }}
            >
              <ScoreRing score={profile.completeness_score} size={52} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: 14.5, fontWeight: 500, color: "var(--ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{profile.google_location_name}</p>
                <p style={{ fontSize: 13, color: "var(--ink-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginTop: 1 }}>{profile.address_city ?? profile.address_formatted ?? "—"}</p>
                <div style={{ display: "flex", gap: 6, marginTop: 5, flexWrap: "wrap" }}>
                  {profile.is_verified && <Badge variant="green">Verified</Badge>}
                  {profile.is_suspended && <Badge variant="red">Suspended</Badge>}
                  {profile.primary_category && <span style={{ fontSize: 11, color: "var(--ink-tertiary)" }}>{profile.primary_category}</span>}
                </div>
              </div>
              <div style={{ textAlign: "right", fontSize: 13, flexShrink: 0 }}>
                <p style={{ fontWeight: 600, color: "var(--ink)" }}>⭐ {profile.average_rating?.toFixed(1) ?? "—"}</p>
                <p style={{ color: "var(--ink-muted)", marginTop: 2 }}>{profile.review_count ?? 0} reviews</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
