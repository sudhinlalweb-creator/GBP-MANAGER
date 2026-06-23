"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"

const NAV = [
  { icon: "dashboard", label: "Dashboard", href: "/dashboard" },
  { icon: "profiles", label: "GBP Profiles", href: "/profiles" },
  { icon: "audit", label: "AI Audit", href: "/audit", badge: "Fin", fin: true },
  { icon: "keywords", label: "Keywords", href: "/keywords" },
  { icon: "reviews", label: "Reviews", href: "/reviews" },
  { icon: "posts", label: "Posts", href: "/posts" },
  { icon: "automation", label: "Automation", href: "/automation" },
  { icon: "agency", label: "Agency", href: "/agency", badge: "Agency" },
  { icon: "settings", label: "Settings", href: "/settings" },
]

function NavIcon({ icon, fin }: { icon: string; fin?: boolean }): JSX.Element {
  const s = { width: 18, height: 18, fill: "none", stroke: fin ? "var(--fin)" : "currentColor", strokeWidth: 1.7, strokeLinecap: "round" as const, strokeLinejoin: "round" as const }
  switch (icon) {
    case "dashboard": return <svg viewBox="0 0 24 24" {...s}><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>
    case "profiles": return <svg viewBox="0 0 24 24" {...s}><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/><path d="M9 9v.01M9 12v.01M9 15v.01"/></svg>
    case "audit": return <svg viewBox="0 0 24 24" {...s}><path d="M9.94 4.06 12 2l2.06 2.06L16 4l-.5 2.5L18 7l-1.5 2L18 11l-2.5.5L16 14l-2-.06L12 16l-2.06-2.06L8 14l.5-2.5L6 11l1.5-2L6 7l2.5-.5z"/></svg>
    case "keywords": return <svg viewBox="0 0 24 24" {...s}><path d="M3 3v18h18"/><rect x="7" y="11" width="3" height="6" rx="1"/><rect x="12" y="7" width="3" height="10" rx="1"/><rect x="17" y="13" width="3" height="4" rx="1"/></svg>
    case "reviews": return <svg viewBox="0 0 24 24" {...s}><path d="M11.5 3.5 14 8.6l5.6.8-4 4 1 5.6-5.1-2.7L6.4 19l1-5.6-4-4 5.6-.8z"/></svg>
    case "posts": return <svg viewBox="0 0 24 24" {...s}><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>
    case "automation": return <svg viewBox="0 0 24 24" {...s}><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>
    case "agency": return <svg viewBox="0 0 24 24" {...s}><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
    case "settings": return <svg viewBox="0 0 24 24" {...s}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1"/></svg>
    default: return <></>
  }
}

export function Sidebar(): JSX.Element {
  const { user, memberships, activeOrgId, setActiveOrg, logout } = useAuth()
  const pathname = usePathname()
  const activeMembership = memberships.find((m) => m.organization_id === activeOrgId)
  const initials = (activeMembership?.organization_name ?? "?").slice(0, 2).toUpperCase()
  const email = user?.email ?? ""
  const emailInitial = email.charAt(0).toUpperCase()

  return (
    <aside style={{
      width: 268, flexShrink: 0, minHeight: "100vh", display: "flex", flexDirection: "column",
      borderRight: "1px solid var(--hairline)", background: "var(--canvas)",
      position: "sticky", top: 0, height: "100vh",
    }}>
      {/* Brand */}
      <div style={{ padding: "24px 20px 18px", display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: "var(--ink)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="var(--canvas)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M9 21v-6h6v6"/></svg>
        </div>
        <span style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.4px", color: "var(--ink)" }}>GBP Manager</span>
      </div>

      {/* Workspace */}
      <div style={{ padding: "0 16px 16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 10, padding: "9px 12px" }}>
          <span style={{ width: 26, height: 26, borderRadius: 7, background: "var(--surface-2)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 12, fontWeight: 600, color: "var(--ink)" }}>{initials}</span>
          <span style={{ flex: 1, minWidth: 0 }}>
            <span style={{ display: "block", fontSize: 13, fontWeight: 500, color: "var(--ink)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{activeMembership?.organization_name ?? "Workspace"}</span>
            <span style={{ display: "block", fontSize: 11, color: "var(--ink-tertiary)" }}>{activeMembership?.role ?? "member"}</span>
          </span>
          {memberships.length > 1 && (
            <select
              value={activeOrgId ?? ""}
              onChange={(e) => setActiveOrg(e.target.value)}
              style={{ position: "absolute", opacity: 0, inset: 0, cursor: "pointer" }}
            >
              {memberships.map((m) => (
                <option key={m.organization_id} value={m.organization_id}>{m.organization_name}</option>
              ))}
            </select>
          )}
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--ink-subtle)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="m7 9 5-5 5 5"/><path d="m7 15 5 5 5-5"/></svg>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, overflowY: "auto", padding: "4px 12px", display: "flex", flexDirection: "column", gap: 2 }}>
        <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.3px", color: "var(--ink-tertiary)", padding: "8px 10px 4px", textTransform: "uppercase" }}>Workspace</span>
        {NAV.map((item) => {
          const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href))
          return (
            <Link key={item.href} href={item.href} style={{
              display: "flex", alignItems: "center", gap: 11, padding: "9px 11px",
              borderRadius: 9, fontSize: 14, fontWeight: 500, textDecoration: "none",
              color: active ? "var(--ink)" : "var(--ink-muted)",
              background: active ? "var(--active-bg)" : "transparent",
              border: `1px solid ${active ? "var(--hairline)" : "transparent"}`,
              transition: "background .15s, color .15s",
            }}>
              <NavIcon icon={item.icon} fin={item.fin} />
              {item.label}
              {item.badge && (
                <span style={{
                  marginLeft: "auto", fontSize: 10, fontWeight: 600, padding: "1px 7px", borderRadius: 999,
                  ...(item.fin ? { background: "var(--fin)", color: "#fff", letterSpacing: "0.2px" } : { color: "var(--ink-muted)", border: "1px solid var(--hairline)" }),
                }}>{item.badge}</span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div style={{ borderTop: "1px solid var(--hairline)", padding: "14px 16px", display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ width: 30, height: 30, borderRadius: 999, background: "var(--fin)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: "#fff", fontSize: 12, fontWeight: 600 }}>{emailInitial}</span>
        <span style={{ flex: 1, minWidth: 0, fontSize: 12.5, fontWeight: 500, color: "var(--ink)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{email}</span>
        <button onClick={() => void logout()} title="Sign out" style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ink-subtle)", display: "flex", padding: 6, borderRadius: 7 }}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></svg>
        </button>
      </div>
    </aside>
  )
}
