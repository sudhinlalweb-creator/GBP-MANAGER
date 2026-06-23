"use client"

import { useEffect, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { Sidebar } from "@/components/layout/sidebar"
import { Spinner } from "@/components/ui/spinner"

export default function ProtectedLayout({ children }: { children: ReactNode }): JSX.Element {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [theme, setTheme] = useState<"light" | "dark">("light")

  useEffect(() => {
    const saved = localStorage.getItem("gbp_theme") as "light" | "dark" | null
    const t = saved ?? "light"
    setTheme(t)
    document.documentElement.setAttribute("data-theme", t)
  }, [])

  useEffect(() => {
    if (!isLoading && !user) router.replace("/login")
  }, [isLoading, user, router])

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark"
    setTheme(next)
    document.documentElement.setAttribute("data-theme", next)
    localStorage.setItem("gbp_theme", next)
  }

  if (isLoading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--canvas)" }}>
        <Spinner size="lg" />
      </div>
    )
  }

  if (!user) return <></>

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--canvas)", color: "var(--ink)", fontFamily: "'Inter', ui-sans-serif, system-ui, sans-serif", WebkitFontSmoothing: "antialiased" }}>
      <Sidebar />
      <main style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        {/* Top header */}
        <header style={{ display: "flex", alignItems: "center", gap: 12, padding: "16px 28px", borderBottom: "1px solid var(--hairline)", background: "var(--canvas)", flexShrink: 0 }}>
          {/* Search */}
          <div style={{ position: "relative", flex: 1, maxWidth: 360 }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--ink-tertiary)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            <input placeholder="Search profiles, reviews…" style={{ width: "100%", fontFamily: "inherit", fontSize: 13.5, color: "var(--ink)", background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 8, padding: "8px 12px 8px 34px", outline: "none" }} />
          </div>
          <div style={{ flex: 1 }} />

          {/* Refresh */}
          <button title="Refresh" onClick={() => window.location.reload()} style={{ background: "var(--surface)", border: "1px solid var(--hairline)", cursor: "pointer", color: "var(--ink-muted)", display: "flex", padding: 8, borderRadius: 8 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 21v-5h5"/></svg>
          </button>

          {/* Notifications */}
          <button title="Notifications" style={{ position: "relative", background: "var(--surface)", border: "1px solid var(--hairline)", cursor: "pointer", color: "var(--ink-muted)", display: "flex", padding: 8, borderRadius: 8 }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            <span style={{ position: "absolute", top: 7, right: 7, width: 6, height: 6, borderRadius: 999, background: "var(--fin)", border: "1.5px solid var(--surface)" }} />
          </button>

          {/* Theme toggle */}
          <button onClick={toggleTheme} title="Toggle theme" style={{ background: "var(--surface)", border: "1px solid var(--hairline)", cursor: "pointer", color: "var(--ink-muted)", display: "flex", padding: 8, borderRadius: 8 }}>
            {theme === "dark"
              ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
              : <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
            }
          </button>

          <div style={{ width: 1, height: 22, background: "var(--hairline)" }} />

          {/* Add profile */}
          <button style={{ display: "flex", alignItems: "center", gap: 7, background: "var(--btn-bg)", color: "var(--btn-fg)", border: "none", borderRadius: 8, padding: "8px 14px", fontFamily: "inherit", fontSize: 13.5, fontWeight: 500, cursor: "pointer", whiteSpace: "nowrap" }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14"/></svg>
            Add profile
          </button>
        </header>

        {/* Page content */}
        <div style={{ padding: "28px", flex: 1, overflowY: "auto" }}>
          {children}
        </div>
      </main>
    </div>
  )
}
