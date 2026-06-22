"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Spinner } from "@/components/ui/spinner"
import { Badge } from "@/components/ui/badge"
import type { Keyword, Project, TargetLocation } from "@/lib/types"

export default function KeywordsPage(): JSX.Element {
  const qc = useQueryClient()
  const [selectedProjectId, setSelectedProjectId] = useState("")
  const [showNewProject, setShowNewProject] = useState(false)
  const [projectName, setProjectName] = useState("")
  const [newKeyword, setNewKeyword] = useState("")
  const [newLocationId, setNewLocationId] = useState("")

  const { data: projects, isLoading: loadingProjects } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => api.get<Project[]>("/projects"),
  })

  const { data: locations } = useQuery<TargetLocation[]>({
    queryKey: ["locations", selectedProjectId],
    queryFn: () => api.get<TargetLocation[]>(`/projects/${selectedProjectId}/locations`),
    enabled: !!selectedProjectId,
  })

  const { data: keywords, isLoading: loadingKeywords } = useQuery<Keyword[]>({
    queryKey: ["keywords", selectedProjectId],
    queryFn: () => api.get<Keyword[]>(`/projects/${selectedProjectId}/keywords`),
    enabled: !!selectedProjectId,
  })

  const createProject = useMutation<Project, Error>({
    mutationFn: () => api.post<Project>("/projects", { name: projectName }),
    onSuccess: (project) => {
      setProjectName("")
      setShowNewProject(false)
      void qc.invalidateQueries({ queryKey: ["projects"] })
      setSelectedProjectId(project.id)
    },
  })

  const addKeyword = useMutation<Keyword, Error>({
    mutationFn: () =>
      api.post<Keyword>(`/projects/${selectedProjectId}/keywords`, {
        phrase: newKeyword,
        target_location_id: newLocationId,
      }),
    onSuccess: () => {
      setNewKeyword("")
      void qc.invalidateQueries({ queryKey: ["keywords", selectedProjectId] })
    },
  })

  const triggerRefresh = useMutation<unknown, Error, string>({
    mutationFn: (kwId) => api.post(`/track/keywords/${kwId}/trigger`),
  })

  const deleteKeyword = useMutation<unknown, Error, string>({
    mutationFn: (kwId) => api.delete(`/projects/${selectedProjectId}/keywords/${kwId}`),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["keywords", selectedProjectId] }),
  })

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-[#f9fafb] text-2xl font-bold">Keyword Tracking</h1>
        <p className="text-gray-400 text-sm mt-1">Track local SERP rankings for your keywords</p>
      </div>

      {/* Projects */}
      <div className="flex items-center gap-3">
        <select
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          className="bg-[#0b1220] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
        >
          <option value="">Select a project…</option>
          {projects?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <button
          onClick={() => setShowNewProject((v) => !v)}
          className="border border-[#1f2937] text-[#f9fafb] px-3 py-2 rounded-lg hover:bg-[#1f2937] transition text-sm"
        >
          + New Project
        </button>
        {loadingProjects && <Spinner size="sm" />}
      </div>

      {showNewProject && (
        <div className="flex gap-2">
          <input
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="Project name"
            className="bg-[#0b1220] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e] flex-1"
          />
          <button
            onClick={() => void createProject.mutate()}
            disabled={createProject.isPending || !projectName}
            className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
          >
            Create
          </button>
        </div>
      )}

      {selectedProjectId && (
        <>
          {/* Add keyword */}
          <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-5 space-y-3">
            <h2 className="text-[#f9fafb] font-medium">Add keyword</h2>
            <div className="flex gap-2">
              <input
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="e.g. plumber near me"
                className="bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e] flex-1"
              />
              <select
                value={newLocationId}
                onChange={(e) => setNewLocationId(e.target.value)}
                className="bg-[#030712] border border-[#1f2937] text-[#f9fafb] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#22c55e]"
              >
                <option value="">Select location…</option>
                {locations?.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.label}
                  </option>
                ))}
              </select>
              <button
                onClick={() => void addKeyword.mutate()}
                disabled={addKeyword.isPending || !newKeyword || !newLocationId}
                className="bg-[#22c55e] text-black font-semibold px-4 py-2 rounded-lg hover:bg-green-400 transition disabled:opacity-60 text-sm"
              >
                Add
              </button>
            </div>
            {locations?.length === 0 && (
              <p className="text-yellow-400 text-xs">
                No locations in this project. Add a location first via the API or Settings.
              </p>
            )}
            {addKeyword.isError && (
              <p className="text-red-400 text-xs">{addKeyword.error.message}</p>
            )}
          </div>

          {/* Keyword list */}
          {loadingKeywords ? (
            <div className="flex justify-center py-6">
              <Spinner />
            </div>
          ) : (
            <div className="space-y-2">
              {keywords?.map((kw) => (
                <div
                  key={kw.id}
                  className="bg-[#0b1220] border border-[#1f2937] rounded-lg px-4 py-3 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant={kw.is_active ? "green" : "gray"}>
                      {kw.is_active ? "Active" : "Paused"}
                    </Badge>
                    <span className="text-[#f9fafb] text-sm font-medium">{kw.phrase}</span>
                    <span className="text-gray-500 text-xs">
                      every {kw.tracking_frequency_minutes / 60}h
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => void triggerRefresh.mutate(kw.id)}
                      disabled={triggerRefresh.isPending}
                      className="text-xs text-[#22c55e] hover:underline"
                    >
                      Refresh
                    </button>
                    <button
                      onClick={() => void deleteKeyword.mutate(kw.id)}
                      className="text-xs text-red-400 hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
              {keywords?.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-6">
                  No keywords yet. Add one above.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
