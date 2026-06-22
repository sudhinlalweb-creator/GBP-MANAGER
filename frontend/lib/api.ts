import { appConfig } from "@/lib/env"
import { getAccessToken, getActiveOrgId } from "@/lib/auth"

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAccessToken()
  const orgId = getActiveOrgId()

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined ?? {}),
  }
  if (token) headers["Authorization"] = `Bearer ${token}`

  // Append org_id query param for org-scoped endpoints
  const separator = path.includes("?") ? "&" : "?"
  const url = orgId ? `${appConfig.apiBaseUrl}${path}${separator}org_id=${orgId}` : `${appConfig.apiBaseUrl}${path}`

  const res = await fetch(url, { ...init, headers, cache: "no-store" })

  if (res.status === 204) return undefined as T

  if (!res.ok) {
    const fallback = `Request failed with status ${res.status}`
    const payload = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(payload?.detail ?? fallback, res.status)
  }

  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
}

// Legacy compat exports
export async function fetchJson<T>(path: string, token: string): Promise<T> {
  const res = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    cache: "no-store",
  })
  if (!res.ok) {
    const payload = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(payload?.detail ?? `Request failed: ${res.status}`, res.status)
  }
  return res.json() as Promise<T>
}

export async function patchJson<TResponse, TPayload>(
  path: string,
  token: string,
  payload: TPayload,
): Promise<TResponse> {
  const res = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  })
  if (!res.ok) {
    const p = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(p?.detail ?? `Request failed: ${res.status}`, res.status)
  }
  return res.json() as Promise<TResponse>
}
