"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react"
import { useRouter } from "next/navigation"
import {
  apiLogin,
  apiLogout,
  apiMe,
  apiRegister,
  clearTokens,
  getAccessToken,
  getActiveOrgId,
  saveTokens,
  setActiveOrgId,
} from "@/lib/auth"
import type { OrganizationMembership, User } from "@/lib/types"

type AuthState = {
  user: User | null
  memberships: OrganizationMembership[]
  activeOrgId: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string, orgName: string) => Promise<void>
  logout: () => Promise<void>
  setActiveOrg: (orgId: string) => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null)
  const [memberships, setMemberships] = useState<OrganizationMembership[]>([])
  const [activeOrgId, setActiveOrgIdState] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const loadMe = useCallback(async () => {
    const token = getAccessToken()
    if (!token) {
      setIsLoading(false)
      return
    }
    try {
      const me = await apiMe(token)
      setUser(me.user)
      setMemberships(me.memberships)
      const stored = getActiveOrgId()
      const valid = me.memberships.find((m) => m.organization_id === stored) ?? me.memberships[0]
      if (valid) {
        setActiveOrgIdState(valid.organization_id)
        setActiveOrgId(valid.organization_id)
      }
    } catch {
      clearTokens()
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadMe()
  }, [loadMe])

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await apiLogin(email, password)
      saveTokens(tokens.access_token, tokens.refresh_token)
      await loadMe()
      router.push("/dashboard")
    },
    [loadMe, router],
  )

  const register = useCallback(
    async (email: string, password: string, fullName: string, orgName: string) => {
      const tokens = await apiRegister(email, password, fullName, orgName)
      saveTokens(tokens.access_token, tokens.refresh_token)
      await loadMe()
      router.push("/dashboard")
    },
    [loadMe, router],
  )

  const logout = useCallback(async () => {
    const token = getAccessToken()
    if (token) await apiLogout(token)
    clearTokens()
    setUser(null)
    setMemberships([])
    setActiveOrgIdState(null)
    router.push("/login")
  }, [router])

  const setActiveOrg = useCallback((orgId: string) => {
    setActiveOrgId(orgId)
    setActiveOrgIdState(orgId)
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, memberships, activeOrgId, isLoading, login, logout, register, setActiveOrg }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider")
  return ctx
}
