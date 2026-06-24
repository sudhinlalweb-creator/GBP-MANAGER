"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { getAccessToken } from "@/lib/auth"

const NAV_LINKS = ["Features", "Pricing", "Agencies", "Blog"]

export function LandingNav() {
  const navRef = useRef<HTMLElement>(null)
  const [authed, setAuthed] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    setAuthed(!!getAccessToken())
    const nav = navRef.current
    if (!nav) return
    const onScroll = () => {
      if (window.scrollY > 12) {
        nav.style.backdropFilter = "saturate(150%) blur(12px)"
        nav.style.borderBottomColor = "#e3ddd4"
        nav.style.background = "rgba(245,241,236,.92)"
      } else {
        nav.style.backdropFilter = "blur(0px)"
        nav.style.borderBottomColor = "transparent"
        nav.style.background = "rgba(245,241,236,.82)"
      }
    }
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("scroll", onScroll)
  }, [])

  useEffect(() => {
    if (menuOpen) document.body.style.overflow = "hidden"
    else document.body.style.overflow = ""
    return () => { document.body.style.overflow = "" }
  }, [menuOpen])

  return (
    <>
      <header
        ref={navRef}
        style={{
          position: "sticky", top: 0, zIndex: 200,
          background: "rgba(245,241,236,.82)",
          backdropFilter: "blur(0px)",
          borderBottom: "1px solid transparent",
          transition: "backdrop-filter .3s, border-color .3s, background .3s",
        }}
      >
        <div className="landing-nav-inner">
          <Link href="/" onClick={() => setMenuOpen(false)}
            style={{ display: "flex", alignItems: "center", gap: 9, fontWeight: 600, fontSize: 19, letterSpacing: "-.4px", color: "#111", textDecoration: "none" }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M12 22s7-6.16 7-12A7 7 0 0 0 5 10c0 5.84 7 12 7 12Z" fill="#111" />
              <circle cx="12" cy="10" r="2.6" fill="#fff" />
            </svg>
            Pinly
          </Link>

          <nav className="landing-nav-links" style={{ fontSize: 14.5, fontWeight: 500 }}>
            {NAV_LINKS.map((label) => (
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
                <Link href="/login" className="landing-nav-login" style={{ fontSize: 14.5, fontWeight: 500, color: "#626260", textDecoration: "none" }}>Log in</Link>
                <Link href="/login" style={{ background: "#111", color: "#fff", fontSize: 14.5, fontWeight: 500, padding: "10px 17px", borderRadius: 8, textDecoration: "none", whiteSpace: "nowrap" }}>
                  Start Free
                </Link>
              </>
            )}
          </div>

          <button
            className="landing-nav-hamburger"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            onClick={() => setMenuOpen((o) => !o)}
            style={{ background: "none", border: "1px solid #d3cec6", borderRadius: 8, width: 42, height: 42, display: "none", alignItems: "center", justifyContent: "center", cursor: "pointer", flexShrink: 0 }}
          >
            {menuOpen
              ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="2.2" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
              : <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="2.2" strokeLinecap="round"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
            }
          </button>
        </div>
      </header>

      {/* Mobile drawer */}
      <div
        className="landing-mobile-overlay"
        onClick={() => setMenuOpen(false)}
        style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.35)", zIndex: 190, opacity: menuOpen ? 1 : 0, pointerEvents: menuOpen ? "auto" : "none", transition: "opacity .25s" }}
      />
      <div
        className="landing-mobile-drawer"
        style={{
          position: "fixed", top: 65, left: 0, right: 0, zIndex: 195,
          background: "#f5f1ec", borderBottom: "1px solid #d3cec6",
          padding: "8px 20px 24px",
          transform: menuOpen ? "translateY(0)" : "translateY(-110%)",
          transition: "transform .3s cubic-bezier(.4,0,.2,1)",
        }}
      >
        <nav style={{ display: "flex", flexDirection: "column" }}>
          {NAV_LINKS.map((label, i) => (
            <a key={label} href={`#${label.toLowerCase()}`}
              onClick={() => setMenuOpen(false)}
              style={{
                fontSize: 17, fontWeight: 500, color: "#111", textDecoration: "none",
                padding: "14px 4px", borderBottom: i < NAV_LINKS.length - 1 ? "1px solid #ebe7e1" : "none",
                display: "flex", alignItems: "center", justifyContent: "space-between",
              }}
            >
              {label}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9c9fa5" strokeWidth="2" strokeLinecap="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </a>
          ))}
        </nav>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 20 }}>
          {authed ? (
            <Link href="/dashboard" onClick={() => setMenuOpen(false)}
              style={{ background: "#111", color: "#fff", fontSize: 16, fontWeight: 600, padding: "14px", borderRadius: 10, textDecoration: "none", textAlign: "center" }}>
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" onClick={() => setMenuOpen(false)}
                style={{ background: "#111", color: "#fff", fontSize: 16, fontWeight: 600, padding: "14px", borderRadius: 10, textDecoration: "none", textAlign: "center" }}>
                Start Free — 14 Days
              </Link>
              <Link href="/login" onClick={() => setMenuOpen(false)}
                style={{ background: "transparent", color: "#111", fontSize: 15, fontWeight: 500, padding: "13px", borderRadius: 10, textDecoration: "none", textAlign: "center", border: "1px solid #d3cec6" }}>
                Log in
              </Link>
            </>
          )}
        </div>
      </div>
    </>
  )
}
