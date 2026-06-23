"use client"

import { useEffect, useRef } from "react"
import Link from "next/link"
import { getAccessToken } from "@/lib/auth"
import { useState } from "react"

export function LandingNav() {
  const navRef = useRef<HTMLElement>(null)
  const [authed, setAuthed] = useState(false)

  useEffect(() => {
    setAuthed(!!getAccessToken())

    const nav = navRef.current
    if (!nav) return
    const onScroll = () => {
      if (window.scrollY > 12) {
        nav.style.backdropFilter = "saturate(150%) blur(12px)"
        nav.style.borderBottomColor = "#e3ddd4"
        nav.style.background = "rgba(245,241,236,.72)"
      } else {
        nav.style.backdropFilter = "blur(0px)"
        nav.style.borderBottomColor = "transparent"
        nav.style.background = "rgba(245,241,236,.82)"
      }
    }
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  return (
    <header
      ref={navRef}
      style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(245,241,236,.82)",
        backdropFilter: "blur(0px)",
        borderBottom: "1px solid transparent",
        transition: "backdrop-filter .3s, border-color .3s, background .3s",
      }}
    >
      <div className="landing-nav-inner">
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 9, fontWeight: 600, fontSize: 19, letterSpacing: "-.4px", color: "#111", textDecoration: "none" }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s7-6.16 7-12A7 7 0 0 0 5 10c0 5.84 7 12 7 12Z" fill="#111" />
            <circle cx="12" cy="10" r="2.6" fill="#fff" />
          </svg>
          Pinly
        </Link>
        <nav className="landing-nav-links" style={{ fontSize: 14.5, fontWeight: 500 }}>
          {["Features", "Pricing", "Agencies", "Blog"].map((label) => (
            <a key={label} href={`#${label.toLowerCase()}`}
              style={{ color: "#626260", textDecoration: "none", transition: "color .2s" }}
              onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "#111" }}
              onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "#626260" }}
            >{label}</a>
          ))}
        </nav>
        <div className="landing-nav-actions">
          {authed ? (
            <Link href="/dashboard" style={{ background: "#111", color: "#fff", fontSize: 14.5, fontWeight: 500, padding: "10px 17px", borderRadius: 8, textDecoration: "none" }}>
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" style={{ fontSize: 14.5, fontWeight: 500, color: "#626260", textDecoration: "none" }}>Log in</Link>
              <Link href="/login" style={{ background: "#111", color: "#fff", fontSize: 14.5, fontWeight: 500, padding: "10px 17px", borderRadius: 8, textDecoration: "none" }}>
                Start Free — 14 Days
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
