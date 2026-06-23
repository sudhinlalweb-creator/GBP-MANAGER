import { appConfig } from "./env"
import type { AuthMe, TokenResponse } from "./types"

const ACCESS_KEY = "gbp_access_token"
const REFRESH_KEY = "gbp_refresh_token"
const ORG_KEY = "gbp_active_org_id"

// ---------------------------------------------------------------------------
// Token storage
// ---------------------------------------------------------------------------

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ACCESS_KEY)
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(REFRESH_KEY)
}

export function getActiveOrgId(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ORG_KEY)
}

export function setActiveOrgId(id: string): void {
  localStorage.setItem(ORG_KEY, id)
}

export function saveTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(ORG_KEY)
  _meCache = null
}

// ---------------------------------------------------------------------------
// Error parsing
// ---------------------------------------------------------------------------

async function parseError(res: Response): Promise<string> {
  const payload = (await res.json().catch(() => null)) as { detail?: unknown } | null
  if (!payload?.detail) return `Request failed (${res.status})`
  if (typeof payload.detail === "string") return payload.detail
  if (Array.isArray(payload.detail)) {
    return (payload.detail as Array<{ msg?: string }>)
      .map((e) => e.msg ?? JSON.stringify(e))
      .join(", ")
  }
  return JSON.stringify(payload.detail)
}

// ---------------------------------------------------------------------------
// Auth API calls (raw fetch — no interceptor to avoid circular deps with api.ts)
// ---------------------------------------------------------------------------

export async function apiLogin(email: string, password: string): Promise<TokenResponse> {
  const form = new URLSearchParams({ username: email, password })
  const res = await fetch(`${appConfig.apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json() as Promise<TokenResponse>
}

export async function apiRegister(
  email: string,
  password: string,
  full_name: string,
  organization_name: string,
): Promise<TokenResponse> {
  const res = await fetch(`${appConfig.apiBaseUrl}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name, organization_name }),
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json() as Promise<TokenResponse>
}

export async function apiRefreshTokens(refreshToken: string): Promise<TokenResponse> {
  const res = await fetch(`${appConfig.apiBaseUrl}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!res.ok) throw new Error("Session expired")
  return res.json() as Promise<TokenResponse>
}

// Backend LogoutRequest expects { refresh_token } in body — NOT the access token in a header
export async function apiLogout(refreshToken: string): Promise<void> {
  await fetch(`${appConfig.apiBaseUrl}/auth/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => {})
}

// ---------------------------------------------------------------------------
// /auth/me with 5-minute in-memory cache
// Prevents a network round-trip on every navigation while auth state is stable.
// Cache is cleared on logout and on token refresh.
// ---------------------------------------------------------------------------

type MeCache = { data: AuthMe; expiresAt: number }
const ME_CACHE_TTL_MS = 5 * 60 * 1000
let _meCache: MeCache | null = null

export function clearMeCache(): void {
  _meCache = null
}

export async function apiMe(token: string): Promise<AuthMe> {
  const now = Date.now()
  if (_meCache && now < _meCache.expiresAt) return _meCache.data

  const res = await fetch(`${appConfig.apiBaseUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })
  if (!res.ok) throw new Error("Unauthorized")

  const data = (await res.json()) as AuthMe
  _meCache = { data, expiresAt: now + ME_CACHE_TTL_MS }
  return data
}

export async function apiForgotPassword(email: string): Promise<void> {
  await fetch(`${appConfig.apiBaseUrl}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
}
