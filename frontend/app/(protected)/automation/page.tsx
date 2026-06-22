"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import type { AutomationRule } from "@/lib/types"

const RULE_TYPES = [
  { value: "auto_reply_positive", label: "Auto-reply (Positive reviews)" },
  { value: "auto_reply_neutral", label: "Auto-reply (Neutral reviews)" },
  { value: "auto_reply_negative", label: "Auto-reply (Negative reviews)" },
]

export default function AutomationPage(): JSX.Element {
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: "", rule_type: "auto_reply_positive", template: "" })
  const { data: rules, isLoading } = useQuery<AutomationRule[]>({
    queryKey: ["automation", activeOrgId],
    queryFn: () => api.get<AutomationRule[]>("/automation"),
    enabled: !!activeOrgId,
  })

  const createMutation = useMutation<AutomationRule, Error>({
    mutationFn: () =>
      api.post<AutomationRule>("/automation", {
        name: form.name,
        rule_type: form.rule_type,
        is_active: true,
        config: { template: form.template },
      }),
    onSuccess: () => {
      setShowForm(false)
      setForm({ name: "", rule_type: "auto_reply_positive", template: "" })
      void qc.invalidateQueries({ queryKey: ["automation"] })
    },
  })

  const toggleMutation = useMutation<AutomationRule, Error, { id: string; is_active: boolean }>({
    mutationFn: ({ id, is_active }) =>
      api.patch<AutomationRule>(`/automation/${id}`, { is_active }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["automation"] }),
  })

  const deleteMutation = useMutation<unknown, Error, string>({
    mutationFn: (id) => api.delete(`/automation/${id}`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["automation"] }),
  })

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#f9fafb] text-2xl font-bold">Automation</h1>
          <p className="text-gray-400 text-sm mt-1">
            Auto-reply rules and scheduled post triggers
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition text-sm"
        >
          {showForm ? "Cancel" : "+ New Rule"}
        </button>
      </div>

      {showForm && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-4">
          <h2 className="text-[#f9fafb] font-semibold">New Automation Rule</h2>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Rule name</label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Thank happy customers"
              className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e]"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Trigger</label>
            <select
              value={form.rule_type}
              onChange={(e) => setForm((f) => ({ ...f, rule_type: e.target.value }))}
              className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
            >
              {RULE_TYPES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Reply template{" "}
              <span className="text-gray-600">(use {"{{author}}"} for reviewer name)</span>
            </label>
            <textarea
              rows={4}
              value={form.template}
              onChange={(e) => setForm((f) => ({ ...f, template: e.target.value }))}
              placeholder="Thank you {{author}} for your wonderful review! We really appreciate your support."
              className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e] resize-none"
            />
          </div>
          {createMutation.isError && (
            <p className="text-red-400 text-sm">{createMutation.error.message}</p>
          )}
          <button
            onClick={() => void createMutation.mutate()}
            disabled={createMutation.isPending || !form.name || !form.template}
            className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
          >
            {createMutation.isPending && <Spinner size="sm" />}
            Create rule
          </button>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      )}

      <div className="space-y-3">
        {rules?.map((rule) => (
          <div
            key={rule.id}
            className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5 flex items-start justify-between gap-4"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={rule.is_active ? "green" : "gray"}>
                  {rule.is_active ? "Active" : "Paused"}
                </Badge>
                <span className="text-[#f9fafb] font-medium">{rule.name}</span>
              </div>
              <p className="text-gray-400 text-sm">
                {RULE_TYPES.find((r) => r.value === rule.rule_type)?.label ?? rule.rule_type}
              </p>
              {rule.config?.template != null && (
                <p className="text-gray-500 text-xs mt-2 line-clamp-2">
                  &ldquo;{String(rule.config.template as string)}&rdquo;
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() =>
                  void toggleMutation.mutate({ id: rule.id, is_active: !rule.is_active })
                }
                disabled={toggleMutation.isPending}
                className="text-xs text-[#22c55e] hover:underline"
              >
                {rule.is_active ? "Pause" : "Enable"}
              </button>
              <button
                onClick={() => void deleteMutation.mutate(rule.id)}
                className="text-xs text-red-400 hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {!isLoading && rules?.length === 0 && (
          <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-10 text-center">
            <p className="text-gray-400">No automation rules yet. Create one to auto-reply to reviews.</p>
          </div>
        )}
      </div>
    </div>
  )
}
