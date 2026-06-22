"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import { ScoreRing } from "@/components/ui/score-ring"
import type { AuditReport, GoogleBusinessProfile } from "@/lib/types"

const PRIORITY_COLOR: Record<string, string> = {
  high: "text-red-400",
  medium: "text-yellow-400",
  low: "text-gray-400",
}

export default function ProfileDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()
  const [runningAudit, setRunningAudit] = useState(false)
  const [auditError, setAuditError] = useState<string | null>(null)

  const { data: profile, isLoading: loadingProfile } = useQuery<GoogleBusinessProfile>({
    queryKey: ["profile", id],
    queryFn: () => api.get<GoogleBusinessProfile>(`/google/profiles/${id}`),
    enabled: !!id,
  })

  const { data: reportsData, isLoading: loadingReports } = useQuery<{
    reports: AuditReport[]
    total: number
  }>({
    queryKey: ["audit-reports", id],
    queryFn: () =>
      api.get<{ reports: AuditReport[]; total: number }>(`/audit/profiles/${id}/reports`),
    enabled: !!id,
  })

  async function runAudit() {
    setRunningAudit(true)
    setAuditError(null)
    try {
      await api.post(`/audit/profiles/${id}/run`)
      setTimeout(() => {
        void qc.invalidateQueries({ queryKey: ["audit-reports", id] })
        setRunningAudit(false)
      }, 3000)
    } catch (err) {
      setAuditError(err instanceof Error ? err.message : "Audit failed")
      setRunningAudit(false)
    }
  }

  const latestReport = reportsData?.reports[0]

  if (loadingProfile) {
    return (
      <div className="flex justify-center py-20">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!profile) {
    return <p className="text-gray-400">Profile not found.</p>
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 flex items-start gap-5">
        <ScoreRing score={profile.completeness_score} size={80} />
        <div className="flex-1">
          <h1 className="text-[#f9fafb] text-xl font-bold">{profile.google_location_name}</h1>
          {profile.address_formatted && (
            <p className="text-gray-400 text-sm mt-1">{profile.address_formatted}</p>
          )}
          <div className="flex flex-wrap gap-2 mt-2">
            {profile.is_verified && <Badge variant="green">Verified</Badge>}
            {profile.is_suspended && <Badge variant="red">Suspended</Badge>}
            {profile.primary_category && (
              <Badge variant="gray">{profile.primary_category}</Badge>
            )}
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
            <div>
              <p className="text-gray-500">Rating</p>
              <p className="text-[#f9fafb] font-medium">
                ⭐ {profile.average_rating?.toFixed(1) ?? "—"}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Reviews</p>
              <p className="text-[#f9fafb] font-medium">{profile.review_count ?? 0}</p>
            </div>
            <div>
              <p className="text-gray-500">Photos</p>
              <p className="text-[#f9fafb] font-medium">—</p>
            </div>
          </div>
        </div>
        <button
          onClick={() => void runAudit()}
          disabled={runningAudit}
          className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm shrink-0"
        >
          {runningAudit && <Spinner size="sm" />}
          {runningAudit ? "Running…" : "Run AI Audit"}
        </button>
      </div>
      {auditError && <p className="text-red-400 text-sm">{auditError}</p>}

      {/* Latest audit */}
      {latestReport && latestReport.status === "completed" && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-4">
          <h2 className="text-[#f9fafb] font-semibold">Latest Audit Score</h2>
          <div className="grid grid-cols-4 gap-4 text-center">
            {[
              { label: "Visibility", score: latestReport.visibility_score },
              { label: "Completeness", score: latestReport.completeness_score },
              { label: "Reviews", score: latestReport.review_score },
              { label: "Engagement", score: latestReport.engagement_score },
            ].map(({ label, score }) => (
              <div key={label} className="flex flex-col items-center gap-2">
                <ScoreRing score={score} size={64} />
                <p className="text-gray-400 text-xs">{label}</p>
              </div>
            ))}
          </div>

          {latestReport.recommendations && latestReport.recommendations.length > 0 && (
            <div className="mt-4 space-y-3">
              <h3 className="text-[#f9fafb] font-medium text-sm">Recommendations</h3>
              {latestReport.recommendations.map((rec, i) => (
                <div key={i} className="bg-[#030712] rounded-lg p-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-[#f9fafb] text-sm font-medium">{rec.title}</p>
                    <span
                      className={`text-xs font-medium uppercase ${PRIORITY_COLOR[rec.priority] ?? "text-gray-400"}`}
                    >
                      {rec.priority}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm mt-1">{rec.description}</p>
                  {rec.action_items.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {rec.action_items.map((item, j) => (
                        <li key={j} className="text-gray-500 text-xs flex gap-2">
                          <span className="text-[#22c55e] shrink-0">→</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Report history */}
      <div>
        <h2 className="text-[#f9fafb] font-semibold mb-3">Audit History</h2>
        {loadingReports && <Spinner />}
        {!loadingReports && (!reportsData?.reports || reportsData.reports.length === 0) && (
          <p className="text-gray-400 text-sm">No audits run yet.</p>
        )}
        <div className="space-y-2">
          {reportsData?.reports.map((report) => (
            <div
              key={report.id}
              className="bg-[#0b1220] border border-[#1f2937] rounded-lg px-4 py-3 flex items-center justify-between text-sm"
            >
              <div className="flex items-center gap-3">
                <Badge
                  variant={
                    report.status === "completed"
                      ? "green"
                      : report.status === "failed"
                        ? "red"
                        : "yellow"
                  }
                >
                  {report.status}
                </Badge>
                <span className="text-gray-400">
                  {new Date(report.created_at).toLocaleString()}
                </span>
              </div>
              {report.visibility_score != null && (
                <span className="text-[#22c55e] font-medium">
                  Score: {report.visibility_score}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
