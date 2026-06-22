"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import { ScoreRing } from "@/components/ui/score-ring"
import type { GoogleBusinessProfile } from "@/lib/types"

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5">
      <p className="text-gray-400 text-sm">{label}</p>
      <p className="text-[#f9fafb] text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}

export default function DashboardPage(): JSX.Element {
  const { activeOrgId } = useAuth()

  const { data: profiles, isLoading } = useQuery<GoogleBusinessProfile[]>({
    queryKey: ["profiles", activeOrgId],
    queryFn: () => api.get<GoogleBusinessProfile[]>("/google/profiles"),
    enabled: !!activeOrgId,
  })

  const connected = profiles?.filter((p) => !p.is_disconnected).length ?? 0
  const avgScore =
    profiles && profiles.length > 0
      ? Math.round(
          profiles.reduce((s, p) => s + (p.completeness_score ?? 0), 0) / profiles.length,
        )
      : null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[#f9fafb] text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Overview of your Google Business Profiles</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Connected Profiles" value={connected} />
        <StatCard label="Avg Completeness" value={avgScore != null ? `${avgScore}%` : "—"} />
        <StatCard
          label="Total Reviews"
          value={profiles?.reduce((s, p) => s + (p.review_count ?? 0), 0) ?? "—"}
        />
        <StatCard
          label="Avg Rating"
          value={
            profiles && profiles.length
              ? (
                  profiles.reduce((s, p) => s + (p.average_rating ?? 0), 0) / profiles.length
                ).toFixed(1)
              : "—"
          }
        />
      </div>

      {/* Profiles */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-[#f9fafb] font-semibold">Business Profiles</h2>
          <Link
            href="/profiles"
            className="text-sm text-[#22c55e] hover:underline"
          >
            View all →
          </Link>
        </div>

        {isLoading && (
          <div className="flex justify-center py-10">
            <Spinner />
          </div>
        )}

        {!isLoading && (!profiles || profiles.length === 0) && (
          <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-10 text-center">
            <p className="text-gray-400 mb-4">No Google Business Profiles connected yet.</p>
            <Link
              href="/profiles"
              className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition text-sm"
            >
              Connect Google Account
            </Link>
          </div>
        )}

        <div className="grid gap-3">
          {profiles?.slice(0, 6).map((profile) => (
            <Link
              key={profile.id}
              href={`/profiles/${profile.id}`}
              className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-4 flex items-center gap-4 hover:border-[#22c55e]/40 transition-colors"
            >
              <ScoreRing score={profile.completeness_score} size={56} />
              <div className="flex-1 min-w-0">
                <p className="text-[#f9fafb] font-medium truncate">
                  {profile.google_location_name}
                </p>
                <p className="text-gray-400 text-sm truncate">
                  {profile.address_city ?? profile.address_formatted ?? "—"}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {profile.is_verified && <Badge variant="green">Verified</Badge>}
                  {profile.is_suspended && <Badge variant="red">Suspended</Badge>}
                  {profile.primary_category && (
                    <span className="text-gray-500 text-xs">{profile.primary_category}</span>
                  )}
                </div>
              </div>
              <div className="text-right text-sm">
                <p className="text-[#f9fafb]">⭐ {profile.average_rating?.toFixed(1) ?? "—"}</p>
                <p className="text-gray-400">{profile.review_count ?? 0} reviews</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
