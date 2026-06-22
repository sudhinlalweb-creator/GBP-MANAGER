"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import type { GoogleBusinessProfile, PostListResponse } from "@/lib/types"

const STATE_VARIANT: Record<string, "green" | "yellow" | "red" | "gray" | "blue"> = {
  published: "green",
  scheduled: "blue",
  failed: "red",
  deleted: "gray",
  pending: "yellow",
}

export default function PostsPage(): JSX.Element {
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()
  const [selectedProfileId, setSelectedProfileId] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    summary: "",
    post_type: "STANDARD",
    call_to_action_type: "",
    call_to_action_url: "",
    scheduled_at: "",
  })

  const { data: profiles } = useQuery<GoogleBusinessProfile[]>({
    queryKey: ["profiles", activeOrgId],
    queryFn: () => api.get<GoogleBusinessProfile[]>("/google/profiles"),
    enabled: !!activeOrgId,
  })

  const { data: postsData, isLoading } = useQuery<PostListResponse>({
    queryKey: ["posts", selectedProfileId],
    queryFn: () => api.get<PostListResponse>(`/posts/profiles/${selectedProfileId}/posts`),
    enabled: !!selectedProfileId,
  })

  const createMutation = useMutation<unknown, Error>({
    mutationFn: () =>
      api.post(`/posts/profiles/${selectedProfileId}/posts`, {
        summary: form.summary,
        post_type: form.post_type,
        call_to_action_type: form.call_to_action_type || null,
        call_to_action_url: form.call_to_action_url || null,
        scheduled_at: form.scheduled_at || null,
      }),
    onSuccess: () => {
      setShowForm(false)
      setForm({ summary: "", post_type: "STANDARD", call_to_action_type: "", call_to_action_url: "", scheduled_at: "" })
      void qc.invalidateQueries({ queryKey: ["posts", selectedProfileId] })
    },
  })

  const deleteMutation = useMutation<unknown, Error, string>({
    mutationFn: (postId) =>
      api.delete(`/posts/profiles/${selectedProfileId}/posts/${postId}`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["posts", selectedProfileId] }),
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#f9fafb] text-2xl font-bold">Posts</h1>
          <p className="text-gray-400 text-sm mt-1">Create and schedule Google Business Profile posts</p>
        </div>
        {selectedProfileId && (
          <button
            onClick={() => setShowForm((v) => !v)}
            className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition text-sm"
          >
            {showForm ? "Cancel" : "+ New Post"}
          </button>
        )}
      </div>

      <select
        value={selectedProfileId}
        onChange={(e) => setSelectedProfileId(e.target.value)}
        className="bg-[#0b1220] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
      >
        <option value="">Select a profile…</option>
        {profiles?.map((p) => (
          <option key={p.id} value={p.id}>
            {p.google_location_name}
          </option>
        ))}
      </select>

      {showForm && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-6 space-y-4">
          <h2 className="text-[#f9fafb] font-semibold">New Post</h2>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Post summary *</label>
            <textarea
              rows={4}
              required
              value={form.summary}
              onChange={(e) => setForm((f) => ({ ...f, summary: e.target.value }))}
              placeholder="What's new with your business?"
              className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e] resize-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Post type</label>
              <select
                value={form.post_type}
                onChange={(e) => setForm((f) => ({ ...f, post_type: e.target.value }))}
                className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              >
                {["STANDARD", "EVENT", "OFFER", "ALERT"].map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Schedule (optional)</label>
              <input
                type="datetime-local"
                value={form.scheduled_at}
                onChange={(e) => setForm((f) => ({ ...f, scheduled_at: e.target.value }))}
                className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Call to action type</label>
              <input
                value={form.call_to_action_type}
                onChange={(e) => setForm((f) => ({ ...f, call_to_action_type: e.target.value }))}
                placeholder="e.g. BOOK, ORDER, LEARN_MORE"
                className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Call to action URL</label>
              <input
                type="url"
                value={form.call_to_action_url}
                onChange={(e) => setForm((f) => ({ ...f, call_to_action_url: e.target.value }))}
                placeholder="https://…"
                className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              />
            </div>
          </div>
          {createMutation.isError && (
            <p className="text-red-400 text-sm">{createMutation.error.message}</p>
          )}
          <button
            onClick={() => void createMutation.mutate()}
            disabled={createMutation.isPending || !form.summary}
            className="flex items-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
          >
            {createMutation.isPending && <Spinner size="sm" />}
            {form.scheduled_at ? "Schedule post" : "Publish now"}
          </button>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      )}

      <div className="space-y-3">
        {postsData?.posts.map((post) => (
          <div
            key={post.id}
            className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={STATE_VARIANT[post.state] ?? "gray"}>{post.state}</Badge>
                  <Badge variant="gray">{post.post_type}</Badge>
                </div>
                <p className="text-[#f9fafb] text-sm">{post.summary}</p>
                {post.scheduled_at && (
                  <p className="text-gray-500 text-xs mt-1">
                    Scheduled: {new Date(post.scheduled_at).toLocaleString()}
                  </p>
                )}
                {post.published_at && (
                  <p className="text-gray-500 text-xs mt-1">
                    Published: {new Date(post.published_at).toLocaleString()}
                  </p>
                )}
              </div>
              {post.state !== "deleted" && (
                <button
                  onClick={() => void deleteMutation.mutate(post.id)}
                  disabled={deleteMutation.isPending}
                  className="text-xs text-red-400 hover:underline shrink-0"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {!isLoading && selectedProfileId && postsData?.posts.length === 0 && (
        <p className="text-gray-400 text-sm text-center py-8">No posts yet. Create your first post above.</p>
      )}
    </div>
  )
}
