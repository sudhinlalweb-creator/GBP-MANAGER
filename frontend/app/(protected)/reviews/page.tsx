"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import type { GoogleBusinessProfile, ReviewListResponse } from "@/lib/types"

function Stars({ rating }: { rating: number | null }): JSX.Element {
  if (rating == null) return <span className="text-gray-500">No rating</span>
  return (
    <span className="text-yellow-400">
      {"★".repeat(rating)}
      <span className="text-gray-600">{"★".repeat(5 - rating)}</span>
    </span>
  )
}

export default function ReviewsPage(): JSX.Element {
  const { activeOrgId } = useAuth()
  const qc = useQueryClient()
  const [selectedProfileId, setSelectedProfileId] = useState<string>("")
  const [replyText, setReplyText] = useState<Record<string, string>>({})
  const [replyingId, setReplyingId] = useState<string | null>(null)

  const { data: profiles } = useQuery<GoogleBusinessProfile[]>({
    queryKey: ["profiles", activeOrgId],
    queryFn: () =>
      api.get<{ profiles: GoogleBusinessProfile[] } | GoogleBusinessProfile[]>("/google/profiles")
        .then((r) => Array.isArray(r) ? r : r.profiles),
    enabled: !!activeOrgId,
  })

  const { data: reviewsData, isLoading } = useQuery<ReviewListResponse>({
    queryKey: ["reviews", selectedProfileId],
    queryFn: () =>
      api.get<ReviewListResponse>(`/reviews/profiles/${selectedProfileId}/reviews`),
    enabled: !!selectedProfileId,
  })

  const syncMutation = useMutation<unknown, Error>({
    mutationFn: () => api.post(`/reviews/profiles/${selectedProfileId}/reviews/sync`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["reviews", selectedProfileId] }),
  })

  const replyMutation = useMutation<unknown, Error, { reviewId: string; text: string }>({
    mutationFn: ({ reviewId, text }) =>
      api.post(`/reviews/profiles/${selectedProfileId}/reviews/${reviewId}/reply`, {
        reply_text: text,
      }),
    onSuccess: (_d, vars) => {
      setReplyText((p) => ({ ...p, [vars.reviewId]: "" }))
      setReplyingId(null)
      void qc.invalidateQueries({ queryKey: ["reviews", selectedProfileId] })
    },
  })

  const deleteReplyMutation = useMutation<unknown, Error, string>({
    mutationFn: (reviewId) =>
      api.delete(`/reviews/profiles/${selectedProfileId}/reviews/${reviewId}/reply`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["reviews", selectedProfileId] }),
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#f9fafb] text-2xl font-bold">Reviews</h1>
          <p className="text-gray-400 text-sm mt-1">Manage and respond to customer reviews</p>
        </div>
        {selectedProfileId && (
          <button
            onClick={() => void syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-2 border border-[#1f2937] text-[#f9fafb] px-4 py-2 rounded-lg hover:bg-[#1f2937] transition text-sm disabled:opacity-50"
          >
            {syncMutation.isPending ? <Spinner size="sm" /> : null}
            Sync reviews
          </button>
        )}
      </div>

      {/* Profile selector */}
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

      {isLoading && (
        <div className="flex justify-center py-10">
          <Spinner />
        </div>
      )}

      {!isLoading && selectedProfileId && reviewsData?.reviews.length === 0 && (
        <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-10 text-center">
          <p className="text-gray-400">No reviews synced yet. Click &ldquo;Sync reviews&rdquo; above.</p>
        </div>
      )}

      <div className="space-y-4">
        {reviewsData?.reviews.map((review) => (
          <div key={review.id} className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-[#f9fafb] font-medium">
                  {review.author_name ?? "Anonymous"}
                </p>
                <div className="flex items-center gap-2 mt-0.5">
                  <Stars rating={review.rating} />
                  {review.sentiment && (
                    <Badge
                      variant={
                        review.sentiment === "positive"
                          ? "green"
                          : review.sentiment === "negative"
                            ? "red"
                            : "gray"
                      }
                    >
                      {review.sentiment}
                    </Badge>
                  )}
                </div>
              </div>
              {review.review_time && (
                <span className="text-gray-500 text-xs shrink-0">
                  {new Date(review.review_time).toLocaleDateString()}
                </span>
              )}
            </div>
            {review.comment && (
              <p className="text-gray-300 text-sm mt-3">{review.comment}</p>
            )}

            {/* Existing reply */}
            {review.reply_text && (
              <div className="mt-3 pl-4 border-l-2 border-[#22c55e]/40">
                <p className="text-gray-500 text-xs mb-1">Your reply</p>
                <p className="text-gray-300 text-sm">{review.reply_text}</p>
                <button
                  onClick={() => void deleteReplyMutation.mutate(review.id)}
                  className="text-xs text-red-400 hover:underline mt-1"
                >
                  Delete reply
                </button>
              </div>
            )}

            {/* Reply form */}
            {!review.reply_text && (
              <div className="mt-3">
                {replyingId === review.id ? (
                  <div className="space-y-2">
                    <textarea
                      rows={3}
                      value={replyText[review.id] ?? ""}
                      onChange={(e) =>
                        setReplyText((p) => ({ ...p, [review.id]: e.target.value }))
                      }
                      placeholder="Write your reply…"
                      className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e] resize-none"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() =>
                          void replyMutation.mutate({
                            reviewId: review.id,
                            text: replyText[review.id] ?? "",
                          })
                        }
                        disabled={replyMutation.isPending || !replyText[review.id]}
                        className="flex items-center gap-1 bg-[#22c55e] text-black text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-green-400 transition disabled:opacity-50"
                      >
                        {replyMutation.isPending && <Spinner size="sm" />}
                        Post reply
                      </button>
                      <button
                        onClick={() => setReplyingId(null)}
                        className="text-xs text-gray-400 hover:text-[#f9fafb]"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setReplyingId(review.id)}
                    className="text-xs text-[#22c55e] hover:underline"
                  >
                    Reply →
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {reviewsData && (
        <p className="text-gray-500 text-sm">
          Showing {reviewsData.reviews.length} of {reviewsData.total} reviews
        </p>
      )}
    </div>
  )
}
