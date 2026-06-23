"use client"

import Link from "next/link"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import { ScoreRing } from "@/components/ui/score-ring"
import type { GoogleAccount, GoogleBusinessProfile } from "@/lib/types"

export default function ProfilesPage(): JSX.Element {
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()

  const { data: accounts, isLoading: loadingAccounts } = useQuery<GoogleAccount[]>({
    queryKey: ["google-accounts", activeOrgId],
    queryFn: () => api.get<GoogleAccount[]>("/google/accounts"),
    enabled: !!activeOrgId,
  })

  const { data: profiles, isLoading: loadingProfiles } = useQuery<GoogleBusinessProfile[]>({
    queryKey: ["profiles", activeOrgId],
    queryFn: () =>
      api.get<{ profiles: GoogleBusinessProfile[] } | GoogleBusinessProfile[]>("/google/profiles")
        .then((r) => Array.isArray(r) ? r : r.profiles),
    enabled: !!activeOrgId,
  })

  const { data: connectData, mutate: connectGoogle, isPending: connecting } = useMutation<
    { authorization_url: string },
    Error
  >({
    mutationFn: () => api.get<{ authorization_url: string }>("/google/connect"),
    onSuccess: (data) => {
      window.location.href = data.authorization_url
    },
  })

  const syncMutation = useMutation<unknown, Error, string>({
    mutationFn: (accountId: string) => api.post(`/google/accounts/${accountId}/sync`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["profiles"] }),
  })

  const loading = loadingAccounts || loadingProfiles

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#f9fafb] text-2xl font-bold">GBP Profiles</h1>
          <p className="text-gray-400 text-sm mt-1">Manage your Google Business Profile locations</p>
        </div>
        <button
          onClick={() => void connectGoogle()}
          disabled={connecting}
          className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
        >
          {connecting ? <Spinner size="sm" /> : null}
          Connect Google Account
        </button>
      </div>

      {/* Connected accounts */}
      {accounts && accounts.length > 0 && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-4">
          <h2 className="text-[#f9fafb] font-medium mb-3 text-sm">Connected Google Accounts</h2>
          <div className="space-y-2">
            {accounts.map((acc) => (
              <div key={acc.id} className="flex items-center justify-between">
                <span className="text-gray-300 text-sm">{acc.google_email}</span>
                <button
                  onClick={() => void syncMutation.mutate(acc.id)}
                  disabled={syncMutation.isPending}
                  className="text-xs text-[#22c55e] hover:underline disabled:opacity-50"
                >
                  {syncMutation.isPending ? "Syncing…" : "Sync now"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      )}

      {!loading && (!profiles || profiles.length === 0) && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-10 text-center">
          <p className="text-gray-400">No profiles yet. Connect a Google account to get started.</p>
        </div>
      )}

      <div className="grid gap-3">
        {profiles?.map((profile) => (
          <Link
            key={profile.id}
            href={`/profiles/${profile.id}`}
            className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5 flex items-start gap-4 hover:border-[#22c55e]/40 transition-colors"
          >
            <ScoreRing score={profile.completeness_score} size={64} />
            <div className="flex-1 min-w-0">
              <p className="text-[#f9fafb] font-semibold">{profile.google_location_name}</p>
              {profile.address_formatted && (
                <p className="text-gray-400 text-sm mt-0.5">{profile.address_formatted}</p>
              )}
              {profile.primary_category && (
                <p className="text-gray-500 text-xs mt-0.5">{profile.primary_category}</p>
              )}
              <div className="flex flex-wrap gap-2 mt-2">
                {profile.is_verified && <Badge variant="green">Verified</Badge>}
                {profile.is_suspended && <Badge variant="red">Suspended</Badge>}
                {profile.is_disconnected && <Badge variant="yellow">Disconnected</Badge>}
                {profile.phone_number && (
                  <span className="text-gray-500 text-xs">{profile.phone_number}</span>
                )}
              </div>
            </div>
            <div className="text-right text-sm shrink-0">
              <p className="text-[#f9fafb] font-medium">
                ⭐ {profile.average_rating?.toFixed(1) ?? "—"}
              </p>
              <p className="text-gray-400">{profile.review_count ?? 0} reviews</p>
              {profile.last_synced_at && (
                <p className="text-gray-600 text-xs mt-1">
                  Synced {new Date(profile.last_synced_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
