import { appConfig } from "./env"
import type { AuthMe, TokenResponse } from "./types"

const ACCESS_KEY = "gbp_access_token"
const REFRESH_KEY = "gbp_refresh_token"
const ORG_KEY = "gbp_active_org_id"

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
}

async function parseError(res: Response): Promise<string> {
  const payload = (await res.json().catch(() => null)) as { detail?: string } | null
  return payload?.detail ?? `Request failed (${res.status})`
}

export async function apiLogin(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${appConfig.apiBaseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
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

export async function apiMe(token: string): Promise<AuthMe> {
  const res = await fetch(`${appConfig.apiBaseUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })
  if (!res.ok) throw new Error("Unauthorized")
  return res.json() as Promise<AuthMe>
}

export async function apiLogout(token: string): Promise<void> {
  await fetch(`${appConfig.apiBaseUrl}/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => {})
}

export async function apiForgotPassword(email: string): Promise<void> {
  await fetch(`${appConfig.apiBaseUrl}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
}
