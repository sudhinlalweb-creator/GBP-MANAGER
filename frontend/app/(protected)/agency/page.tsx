"use client"

import { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge, planBadgeVariant } from "@/components/ui/badge"
import type { AgencyBranding, AgencyDashboard, ClientLink } from "@/lib/types"

type Tab = "dashboard" | "clients" | "branding"

export default function AgencyPage(): JSX.Element {
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()
  const [tab, setTab] = useState<Tab>("dashboard")
  const [newClientId, setNewClientId] = useState("")
  const [brandingForm, setBrandingForm] = useState<Partial<AgencyBranding>>({})

  const { data: dashboard, isLoading: loadingDashboard } = useQuery<AgencyDashboard>({
    queryKey: ["agency-dashboard", activeOrgId],
    queryFn: () => api.get<AgencyDashboard>("/agency/dashboard"),
    enabled: !!activeOrgId && tab === "dashboard",
  })

  const { data: clients, isLoading: loadingClients } = useQuery<ClientLink[]>({
    queryKey: ["agency-clients", activeOrgId],
    queryFn: () => api.get<ClientLink[]>("/agency/clients"),
    enabled: !!activeOrgId && tab === "clients",
  })

  const { data: branding } = useQuery<AgencyBranding>({
    queryKey: ["agency-branding", activeOrgId],
    queryFn: () => api.get<AgencyBranding>("/agency/branding"),
    enabled: !!activeOrgId && tab === "branding",
  })

  useEffect(() => {
    if (branding) setBrandingForm(branding)
  }, [branding])

  const addClientMutation = useMutation<ClientLink, Error>({
    mutationFn: () =>
      api.post<ClientLink>("/agency/clients", { client_org_id: newClientId }),
    onSuccess: () => {
      setNewClientId("")
      void qc.invalidateQueries({ queryKey: ["agency-clients"] })
    },
  })

  const removeClientMutation = useMutation<unknown, Error, string>({
    mutationFn: (clientOrgId) => api.delete(`/agency/clients/${clientOrgId}`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["agency-clients"] }),
  })

  const updateBrandingMutation = useMutation<AgencyBranding, Error>({
    mutationFn: () => api.patch<AgencyBranding>("/agency/branding", brandingForm),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["agency-branding"] }),
  })

  const TABS: { key: Tab; label: string }[] = [
    { key: "dashboard", label: "Dashboard" },
    { key: "clients", label: "Clients" },
    { key: "branding", label: "White-label" },
  ]

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-[#f9fafb] text-2xl font-bold">Agency</h1>
        <p className="text-gray-400 text-sm mt-1">
          Manage client accounts and white-label branding
        </p>
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

      {/* Dashboard tab */}
      {tab === "dashboard" && (
        <>
          {loadingDashboard && (
            <div className="flex justify-center py-10">
              <Spinner />
            </div>
          )}
          {dashboard && (
            <>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: "Total clients", value: dashboard.total_clients },
                  { label: "Total locations", value: dashboard.total_locations },
                  {
                    label: "Avg visibility score",
                    value: dashboard.avg_visibility_score?.toFixed(1) ?? "—",
                  },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5">
                    <p className="text-gray-400 text-sm">{label}</p>
                    <p className="text-[#f9fafb] text-2xl font-bold mt-1">{value}</p>
                  </div>
                ))}
              </div>
              <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#1f2937]">
                      {["Client", "Plan", "Locations", "Avg Score", "Open Reviews", "Last Audit"].map(
                        (h) => (
                          <th
                            key={h}
                            className="px-4 py-3 text-left text-gray-400 font-medium"
                          >
                            {h}
                          </th>
                        ),
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.clients.map((client) => (
                      <tr
                        key={client.client_org_id}
                        className="border-b border-[#1f2937] last:border-0"
                      >
                        <td className="px-4 py-3 text-[#f9fafb] font-medium">
                          {client.client_org_name}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={planBadgeVariant(client.plan)}>{client.plan}</Badge>
                        </td>
                        <td className="px-4 py-3 text-gray-300">{client.location_count}</td>
                        <td className="px-4 py-3 text-gray-300">
                          {client.avg_visibility_score?.toFixed(1) ?? "—"}
                        </td>
                        <td className="px-4 py-3 text-gray-300">{client.open_review_count}</td>
                        <td className="px-4 py-3 text-gray-500 text-xs">
                          {client.last_audit_at
                            ? new Date(client.last_audit_at).toLocaleDateString()
                            : "Never"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {dashboard.clients.length === 0 && (
                  <p className="text-gray-400 text-sm text-center py-8">No clients yet.</p>
                )}
              </div>
            </>
          )}
        </>
      )}

      {/* Clients tab */}
      {tab === "clients" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              value={newClientId}
              onChange={(e) => setNewClientId(e.target.value)}
              placeholder="Client organization ID (UUID)"
              className="flex-1 bg-[#0b1220] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
            />
            <button
              onClick={() => void addClientMutation.mutate()}
              disabled={addClientMutation.isPending || !newClientId}
              className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
            >
              {addClientMutation.isPending && <Spinner size="sm" />}
              Add client
            </button>
          </div>
          {loadingClients ? (
            <Spinner />
          ) : (
            <div className="space-y-2">
              {clients?.map((link) => (
                <div
                  key={link.id}
                  className="bg-[#0b1220] border border-[#1f2937] rounded-xl px-4 py-3 flex items-center justify-between"
                >
                  <div>
                    <span className="text-[#f9fafb] font-medium">{link.client_org_name}</span>
                    <Badge variant={planBadgeVariant(link.client_org_plan)} >{link.client_org_plan}</Badge>
                  </div>
                  <button
                    onClick={() => void removeClientMutation.mutate(link.client_org_id)}
                    className="text-xs text-red-400 hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ))}
              {clients?.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-6">No clients linked yet.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Branding tab */}
      {tab === "branding" && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-4">
          <h2 className="text-[#f9fafb] font-semibold">White-label Branding</h2>
          {[
            { key: "agency_name", label: "Agency name", type: "text", placeholder: "Your Agency Name" },
            { key: "logo_url", label: "Logo URL", type: "url", placeholder: "https://…" },
            { key: "brand_color", label: "Brand color (hex)", type: "text", placeholder: "#22c55e" },
            { key: "custom_domain", label: "Custom domain", type: "text", placeholder: "app.youragency.com" },
            { key: "reply_from_email", label: "Reply-from email", type: "email", placeholder: "reports@youragency.com" },
          ].map(({ key, label, type, placeholder }) => (
            <div key={key}>
              <label className="block text-sm text-gray-400 mb-1">{label}</label>
              <input
                type={type}
                value={String(brandingForm[key as keyof AgencyBranding] ?? "")}
                onChange={(e) =>
                  setBrandingForm((f) => ({ ...f, [key]: e.target.value || null }))
                }
                placeholder={placeholder}
                className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              />
            </div>
          ))}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Report footer</label>
            <textarea
              rows={2}
              value={String(brandingForm.report_footer_text ?? "")}
              onChange={(e) =>
                setBrandingForm((f) => ({ ...f, report_footer_text: e.target.value || null }))
              }
              placeholder="Powered by Your Agency"
              className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e] resize-none"
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={brandingForm.hide_platform_branding ?? false}
              onChange={(e) =>
                setBrandingForm((f) => ({ ...f, hide_platform_branding: e.target.checked }))
              }
              className="accent-[#22c55e]"
            />
            <span className="text-gray-300 text-sm">Hide &ldquo;Powered by GBP Manager&rdquo;</span>
          </label>
          <button
            onClick={() => void updateBrandingMutation.mutate()}
            disabled={updateBrandingMutation.isPending}
            className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
          >
            {updateBrandingMutation.isPending && <Spinner size="sm" />}
            Save branding
          </button>
          {updateBrandingMutation.isSuccess && (
            <p className="text-[#22c55e] text-sm">Saved!</p>
          )}
        </div>
      )}
    </div>
  )
}
