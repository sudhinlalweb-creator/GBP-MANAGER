"use client"

import { useEffect, useRef } from "react"
import Link from "next/link"

function AuditCard() {
  const gaugeRef = useRef<SVGCircleElement>(null)
  const numRef = useRef<HTMLSpanElement>(null)
  const labelRef = useRef<HTMLDivElement>(null)
  const afterRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const full = 377
    const target = 91
    const dur = 1800
    const start = performance.now()
    const colorFor = (s: number) => s < 50 ? "#c41c1c" : s < 75 ? "#f59e0b" : "#0bdf50"
    const labelFor = (s: number) => s < 50 ? "POOR" : s < 75 ? "FAIR" : "EXCELLENT"
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / dur)
      const e = 1 - Math.pow(1 - t, 3)
      const v = target * e
      const c = colorFor(v)
      if (gaugeRef.current) { gaugeRef.current.style.strokeDashoffset = String(full - (full * v / 100)); gaugeRef.current.style.stroke = c }
      if (numRef.current) numRef.current.textContent = String(Math.round(v))
      if (afterRef.current) afterRef.current.textContent = String(Math.round(v))
      if (labelRef.current) { labelRef.current.textContent = labelFor(v); labelRef.current.style.color = c }
      if (t < 1) requestAnimationFrame(tick)
    }
    const id = setTimeout(() => requestAnimationFrame(tick), 400)
    return () => clearTimeout(id)
  }, [])

  return (
    <div style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 16, padding: 26 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
          <div style={{ width: 38, height: 38, borderRadius: 9, background: "#f5f1ec", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M12 21s7-6.16 7-12A7 7 0 0 0 5 9c0 5.84 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/></svg>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15, letterSpacing: "-.2px" }}>Amend Dental Clinic</div>
            <div style={{ fontSize: 12.5, color: "#7b7b78" }}>GBP Audit · live scan</div>
          </div>
        </div>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: ".4px", color: "#0bdf50", display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#0bdf50", display: "inline-block", animation: "pinly-pulse 1.4s infinite" }} />
          LIVE
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 22, padding: "18px 4px 8px" }}>
        <div style={{ position: "relative", width: 148, height: 148, flexShrink: 0 }}>
          <svg width="148" height="148" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="80" fill="none" stroke="#ebe7e1" strokeWidth="15" strokeLinecap="round" strokeDasharray="377 503" transform="rotate(135 100 100)" />
            <circle ref={gaugeRef} cx="100" cy="100" r="80" fill="none" stroke="#0bdf50" strokeWidth="15" strokeLinecap="round" strokeDasharray="377 503" strokeDashoffset={377} transform="rotate(135 100 100)" style={{ transition: "none" }} />
          </svg>
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ fontSize: 38, fontWeight: 600, letterSpacing: "-1.5px", lineHeight: 1 }}>
              <span ref={numRef}>0</span><span style={{ fontSize: 17, color: "#9c9fa5", fontWeight: 500 }}>/100</span>
            </div>
            <div ref={labelRef} style={{ fontSize: 11.5, fontWeight: 600, color: "#9c9fa5", marginTop: 3, letterSpacing: ".3px" }}>SCANNING</div>
          </div>
        </div>
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 13 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#edfaf1", border: "1px solid #c7efd3", borderRadius: 9999, padding: "5px 11px 5px 9px", alignSelf: "flex-start", fontSize: 12.5, fontWeight: 600, color: "#0a8f3c" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0a8f3c" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 17l6-6 4 4 8-8M21 7v6h-6"/></svg>
            +57 points after fixes
          </div>
          <div style={{ display: "flex", alignItems: "stretch", gap: 9 }}>
            <div style={{ flex: 1, background: "#faf7f3", border: "1px solid #ebe7e1", borderRadius: 10, padding: "10px 12px" }}>
              <div style={{ fontSize: 10.5, letterSpacing: ".4px", textTransform: "uppercase", color: "#9c9fa5", fontWeight: 600, marginBottom: 4 }}>Before</div>
              <div style={{ fontSize: 23, fontWeight: 600, color: "#9c9fa5", letterSpacing: "-.6px", lineHeight: 1 }}>34</div>
            </div>
            <div style={{ display: "flex", alignItems: "center", color: "#c7c2b8" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </div>
            <div style={{ flex: 1, background: "#f0fbf4", border: "1px solid #c7efd3", borderRadius: 10, padding: "10px 12px" }}>
              <div style={{ fontSize: 10.5, letterSpacing: ".4px", textTransform: "uppercase", color: "#0a8f3c", fontWeight: 600, marginBottom: 4 }}>After</div>
              <div style={{ fontSize: 23, fontWeight: 600, color: "#0bdf50", letterSpacing: "-.6px", lineHeight: 1 }}><span ref={afterRef}>34</span></div>
            </div>
          </div>
        </div>
      </div>
      <div style={{ borderTop: "1px solid #ebe7e1", marginTop: 10, paddingTop: 14, display: "flex", flexDirection: "column", gap: 11 }}>
        {[
          { icon: "check", label: "Profile completeness", val: "100%", color: "#0bdf50" },
          { icon: "check", label: "Review response rate", val: "98%", color: "#0bdf50" },
          { icon: "warn", label: "Post frequency", val: "Needs attention", color: "#ff5600" },
          { icon: "check", label: "Keyword optimization", val: "Strong", color: "#0bdf50" },
        ].map(({ icon, label, val, color }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              {icon === "check"
                ? <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                : <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>
              }
              {label}
            </div>
            <span style={{ fontWeight: 600, color }}>{val}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function HeroSection() {
  return (
    <section style={{ maxWidth: 1200, margin: "0 auto", padding: "56px 24px 56px", display: "grid", gridTemplateColumns: "1.05fr .95fr", gap: 56, alignItems: "center" }}>
      <div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#fff", border: "1px solid #d3cec6", borderRadius: 9999, padding: "6px 14px", fontSize: 13, fontWeight: 500, color: "#626260", marginBottom: 24 }}>
          <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#0bdf50", display: "inline-block" }} />
          Trusted by 2,400+ local businesses across India
        </div>
        <h1 style={{ fontSize: "clamp(40px,5vw,60px)", lineHeight: 1.04, letterSpacing: "-2px", fontWeight: 600, maxWidth: 620 }}>
          Your competitors are ranking on Google Maps.{" "}
          <span style={{ color: "#626260" }}>You should be too.</span>
        </h1>
        <p style={{ fontSize: 19, lineHeight: 1.5, color: "#626260", marginTop: 24, maxWidth: 520, letterSpacing: "-.1px" }}>
          Pinly audits, optimizes, and auto-manages your Google Business Profile so you show up first — for every local search that matters.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 34, flexWrap: "wrap" }}>
          <Link href="/login" style={{ background: "#111", color: "#fff", fontSize: 15, fontWeight: 500, padding: "13px 22px", borderRadius: 8, textDecoration: "none" }}>
            Start Free Trial
          </Link>
          <a href="#how" style={{ background: "#fff", color: "#111", fontSize: 15, fontWeight: 500, padding: "13px 22px", borderRadius: 8, border: "1px solid #d3cec6", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 8 }}>
            See how it works
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </a>
        </div>
        <div style={{ marginTop: 30, display: "flex", alignItems: "center", gap: 10, fontSize: 13.5, color: "#7b7b78" }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0bdf50" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
          No credit card required · Setup in 3 minutes
        </div>
      </div>
      <AuditCard />
    </section>
  )
}
