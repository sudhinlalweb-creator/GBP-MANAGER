import { appConfig } from "@/lib/env"
import {
  clearMeCache,
  clearTokens,
  getAccessToken,
  getActiveOrgId,
  getRefreshToken,
  apiRefreshTokens,
  saveTokens,
} from "@/lib/auth"

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

// ---------------------------------------------------------------------------
// Concurrent refresh deduplication
// If multiple requests fail with 401 simultaneously, only one refresh call
// is made. All waiting callers receive the same new access token.
// ---------------------------------------------------------------------------

let _refreshPromise: Promise<string> | null = null

async function _attemptTokenRefresh(): Promise<string> {
  if (_refreshPromise) return _refreshPromise

  _refreshPromise = (async () => {
    const refreshToken = getRefreshToken()
    if (!refreshToken) throw new Error("No refresh token available")
    const tokens = await apiRefreshTokens(refreshToken)
    saveTokens(tokens.access_token, tokens.refresh_token)
    clearMeCache()
    return tokens.access_token
  })().finally(() => {
    _refreshPromise = null
  })

  return _refreshPromise
}

function _redirectToLogin(): void {
  clearTokens()
  if (typeof window !== "undefined") {
    window.location.href = "/login"
  }
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function _rawFetch(path: string, init: RequestInit, token: string | null): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined ?? {}),
  }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const orgId = getActiveOrgId()
  const separator = path.includes("?") ? "&" : "?"
  const url = orgId
    ? `${appConfig.apiBaseUrl}${path}${separator}org_id=${orgId}`
    : `${appConfig.apiBaseUrl}${path}`

  return fetch(url, { ...init, headers, cache: "no-store" })
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken()
  let res = await _rawFetch(path, init, token)

  // 401 — try refreshing once, then retry the original request
  if (res.status === 401) {
    try {
      const newToken = await _attemptTokenRefresh()
      res = await _rawFetch(path, init, newToken)
    } catch {
      _redirectToLogin()
      throw new ApiError("Session expired. Please log in again.", 401)
    }
  }

  if (res.status === 204) return undefined as T

  if (!res.ok) {
    const fallback = `Request failed with status ${res.status}`
    const payload = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(payload?.detail ?? fallback, res.status)
  }

  return res.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// Legacy compat — used only by dead components (phase-two-dashboard, admin-panel)
// Remove these when those components are deleted in the tech debt pass.
// ---------------------------------------------------------------------------

export async function fetchJson<T>(path: string, _token: string): Promise<T> {
  return request<T>(path)
}

export async function patchJson<TResponse, TPayload>(
  path: string,
  _token: string,
  payload: TPayload,
): Promise<TResponse> {
  return request<TResponse>(path, { method: "PATCH", body: JSON.stringify(payload) })
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
}
