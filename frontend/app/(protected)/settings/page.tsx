"use client"

import { useState } from "react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge, planBadgeVariant } from "@/components/ui/badge"
import type { Organization } from "@/lib/types"

type Tab = "org" | "billing" | "members"

export default function SettingsPage(): JSX.Element {
  const { activeOrgId, memberships } = useAuth()
  const [tab, setTab] = useState<Tab>("org")
  const [inviteEmail, setInviteEmail] = useState("")
  const [inviteSent, setInviteSent] = useState(false)

  const { data: org, isLoading } = useQuery<Organization>({
    queryKey: ["org", activeOrgId],
    queryFn: () => api.get<Organization>(`/organizations/${activeOrgId ?? ""}`),
    enabled: !!activeOrgId,
  })

  const checkoutMutation = useMutation<{ url: string }, Error, string>({
    mutationFn: (plan) =>
      api.post<{ url: string }>("/billing/checkout", { plan, success_url: window.location.href, cancel_url: window.location.href }),
    onSuccess: (data) => {
      window.location.href = data.url
    },
  })

  const portalMutation = useMutation<{ url: string }, Error>({
    mutationFn: () =>
      api.post<{ url: string }>("/billing/portal", { return_url: window.location.href }),
    onSuccess: (data) => {
      window.location.href = data.url
    },
  })

  const inviteMutation = useMutation<unknown, Error>({
    mutationFn: () =>
      api.post(`/organizations/${activeOrgId ?? ""}/invite`, { email: inviteEmail }),
    onSuccess: () => {
      setInviteSent(true)
      setInviteEmail("")
    },
  })

  const TABS: { key: Tab; label: string }[] = [
    { key: "org", label: "Organization" },
    { key: "billing", label: "Billing" },
    { key: "members", label: "Members" },
  ]

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-[#f9fafb] text-2xl font-bold">Settings</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your organization and billing</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[#1f2937]">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.key
                ? "text-[#22c55e] border-b-2 border-[#22c55e]"
                : "text-gray-400 hover:text-[#f9fafb]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "org" && org && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Organization name</p>
              <p className="text-[#f9fafb] font-semibold text-lg">{org.name}</p>
            </div>
            <Badge variant={planBadgeVariant(org.plan)}>{org.plan}</Badge>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-[#030712] rounded-lg p-3">
              <p className="text-gray-500">Location limit</p>
              <p className="text-[#f9fafb] font-medium mt-0.5">{org.location_limit}</p>
            </div>
            <div className="bg-[#030712] rounded-lg p-3">
              <p className="text-gray-500">Keyword limit</p>
              <p className="text-[#f9fafb] font-medium mt-0.5">{org.keyword_limit}</p>
            </div>
            <div className="bg-[#030712] rounded-lg p-3">
              <p className="text-gray-500">Subscription status</p>
              <p className="text-[#f9fafb] font-medium mt-0.5">{org.subscription_status}</p>
            </div>
            <div className="bg-[#030712] rounded-lg p-3">
              <p className="text-gray-500">Plan</p>
              <p className="text-[#f9fafb] font-medium mt-0.5 capitalize">{org.plan}</p>
            </div>
          </div>
        </div>
      )}

      {tab === "billing" && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-5">
          <h2 className="text-[#f9fafb] font-semibold">Plans</h2>
          <div className="grid gap-3">
            {[
              { plan: "starter", label: "Starter", price: "$29/mo", features: ["5 locations", "50 keywords", "AI audits"] },
              { plan: "pro", label: "Pro", price: "$79/mo", features: ["20 locations", "200 keywords", "Priority AI"] },
              { plan: "agency", label: "Agency", price: "$199/mo", features: ["Unlimited", "White-label", "Client reports"] },
            ].map(({ plan, label, price, features }) => (
              <div
                key={plan}
                className={`border rounded-xl p-4 flex items-center justify-between ${
                  org?.plan === plan
                    ? "border-[#22c55e] bg-[#22c55e]/5"
                    : "border-[#1f2937]"
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[#f9fafb] font-medium">{label}</span>
                    {org?.plan === plan && (
                      <Badge variant="green">Current</Badge>
                    )}
                  </div>
                  <p className="text-[#22c55e] font-bold mt-0.5">{price}</p>
                  <p className="text-gray-500 text-xs mt-1">{features.join(" · ")}</p>
                </div>
                {org?.plan !== plan && (
                  <button
                    onClick={() => void checkoutMutation.mutate(plan)}
                    disabled={checkoutMutation.isPending}
                    className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
                  >
                    Upgrade
                  </button>
                )}
              </div>
            ))}
          </div>
          {org?.plan !== "trial" && (
            <button
              onClick={() => void portalMutation.mutate()}
              disabled={portalMutation.isPending}
              className="flex items-center gap-2 border border-[#1f2937] text-[#f9fafb] px-4 py-2 rounded-lg hover:bg-[#1f2937] transition text-sm"
            >
              {portalMutation.isPending && <Spinner size="sm" />}
              Manage billing →
            </button>
          )}
        </div>
      )}

      {tab === "members" && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-5">
          <h2 className="text-[#f9fafb] font-semibold">Team Members</h2>
          <div className="space-y-2">
            {memberships.map((m) => (
              <div
                key={m.id}
                className="flex items-center justify-between py-2 border-b border-[#1f2937] last:border-0"
              >
                <span className="text-gray-300 text-sm">{m.user_id.slice(0, 16)}…</span>
                <Badge variant={m.role === "owner" ? "green" : "gray"}>{m.role}</Badge>
              </div>
            ))}
          </div>
          <div className="pt-2">
            <h3 className="text-[#f9fafb] font-medium text-sm mb-3">Invite member</h3>
            {inviteSent ? (
              <p className="text-[#22c55e] text-sm">Invite sent!</p>
            ) : (
              <div className="flex gap-2">
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@example.com"
                  className="flex-1 bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
                />
                <button
                  onClick={() => void inviteMutation.mutate()}
                  disabled={inviteMutation.isPending || !inviteEmail}
                  className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
                >
                  {inviteMutation.isPending && <Spinner size="sm" />}
                  Invite
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
