"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { Badge, planBadgeVariant } from "@/components/ui/badge"

type NavItem = {
  href: string
  label: string
  icon: JSX.Element
  plans?: string[]
}

function HomeIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
}
function BuildingIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
}
function SparklesIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
}
function ChartIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
}
function StarIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
}
function EditIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
}
function BoltIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
}
function BriefcaseIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
}
function CogIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
}
function LogoutIcon(): JSX.Element {
  return <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
}

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: <HomeIcon /> },
  { href: "/profiles", label: "GBP Profiles", icon: <BuildingIcon /> },
  { href: "/audit", label: "AI Audit", icon: <SparklesIcon /> },
  { href: "/keywords", label: "Keywords", icon: <ChartIcon /> },
  { href: "/reviews", label: "Reviews", icon: <StarIcon /> },
  { href: "/posts", label: "Posts", icon: <EditIcon /> },
  { href: "/automation", label: "Automation", icon: <BoltIcon /> },
  { href: "/agency", label: "Agency", icon: <BriefcaseIcon />, plans: ["agency"] },
  { href: "/settings", label: "Settings", icon: <CogIcon /> },
]

export function Sidebar(): JSX.Element {
  const pathname = usePathname()
  const { user, memberships, activeOrgId, setActiveOrg, logout } = useAuth()

  const activeMembership = memberships.find((m) => m.organization_id === activeOrgId)

  return (
    <aside className="w-56 min-h-screen bg-[#0b1220] border-r border-[#1f2937] flex flex-col">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-[#1f2937]">
        <span className="text-[#22c55e] font-bold text-lg tracking-tight">GBP Manager</span>
      </div>

      {/* Org switcher */}
      {memberships.length > 0 && (
        <div className="px-3 py-3 border-b border-[#1f2937]">
          <select
            value={activeOrgId ?? ""}
            onChange={(e) => setActiveOrg(e.target.value)}
            className="w-full bg-[#030712] border border-[#1f2937] text-[#f9fafb] text-xs rounded px-2 py-1.5 focus:outline-none focus:border-[#22c55e]"
          >
            {memberships.map((m) => (
              <option key={m.organization_id} value={m.organization_id}>
                {m.organization_id.slice(0, 8)}… ({m.role})
              </option>
            ))}
          </select>
          {activeMembership && (
            <p className="text-gray-500 text-xs mt-1 px-1">{activeMembership.role}</p>
          )}
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-[#22c55e]/10 text-[#22c55e]"
                  : "text-gray-400 hover:text-[#f9fafb] hover:bg-[#1f2937]/50"
              }`}
            >
              {item.icon}
              {item.label}
              {item.plans && (
                <span className="ml-auto text-[10px] text-blue-400 border border-blue-800 rounded px-1">
                  Agency
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* User */}
      <div className="px-3 py-3 border-t border-[#1f2937]">
        <p className="text-xs text-gray-400 truncate mb-2">{user?.email}</p>
        <button
          onClick={() => void logout()}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-red-400 transition-colors"
        >
          <LogoutIcon />
          Sign out
        </button>
      </div>
    </aside>
  )
}
