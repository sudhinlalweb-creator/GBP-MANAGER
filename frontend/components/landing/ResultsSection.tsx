"use client"

import { useEffect, useRef } from "react"

const STATS = [
  { count: 2400, suffix: "+", label: "Businesses optimized" },
  { count: 41, suffix: "%", label: "Avg. ranking lift in 90 days", green: true },
  { count: 3.2, suffix: "x", label: "More profile views", decimals: 1 },
  { count: 98, suffix: "%", label: "Customer satisfaction" },
]

const TESTIMONIALS = [
  {
    quote: "We went from page 3 to the top 3 in our city within 6 weeks. Our walk-ins increased by 40%.",
    initials: "RM", name: "Rohan M.", role: "Restaurant Owner, Bangalore",
  },
  {
    quote: "Managing 12 clinic locations used to take hours every week. Now it's one dashboard, 20 minutes.",
    initials: "PS", name: "Dr. Priya S.", role: "Multi-location Clinic, Mumbai",
  },
  {
    quote: "The AI post scheduler alone saved us 8 hours a month. The ranking gains were a bonus.",
    initials: "AK", name: "Amit K.", role: "Digital Marketing Agency, Delhi",
  },
]

function StatCard({ count, suffix, label, green, decimals }: { count: number; suffix: string; label: string; green?: boolean; decimals?: number }) {
  const spanRef = useRef<HTMLSpanElement>(null)
  const animated = useRef(false)

  useEffect(() => {
    const el = spanRef.current
    if (!el) return
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !animated.current) {
        animated.current = true
        const dur = 1400
        const start = performance.now()
        const fmt = (n: number) => decimals ? n.toFixed(decimals) : Math.round(n).toLocaleString("en-IN")
        const tick = (now: number) => {
          const t = Math.min(1, (now - start) / dur)
          const e = 1 - Math.pow(1 - t, 3)
          el.textContent = fmt(count * e) + suffix
          if (t < 1) requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
        obs.disconnect()
      }
    }, { threshold: 0.2 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [count, suffix, decimals])

  return (
    <div style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 14, padding: "22px 20px", display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ fontSize: 42, fontWeight: 700, letterSpacing: "-2px", lineHeight: 1, color: green ? "#0bdf50" : "#111" }}>
        <span ref={spanRef}>0{suffix}</span>
      </div>
      <div style={{ fontSize: 13.5, color: "#626260", lineHeight: 1.4 }}>{label}</div>
    </div>
  )
}

export function ResultsSection() {
  return (
    <section id="agencies" className="landing-section" style={{ scrollMarginTop: 80 }}>
      <div style={{ maxWidth: 680, marginBottom: 44 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>Results</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600, margin: 0 }}>
          Real businesses. Real results.
        </h2>
      </div>

      {/* Stats grid — 2 col on mobile, 4 col desktop */}
      <div className="results-stats-grid">
        {STATS.map((s) => <StatCard key={s.label} {...s} />)}
      </div>

      {/* Testimonials */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 20 }}>
        {TESTIMONIALS.map(({ quote, initials, name, role }) => (
          <div key={name} style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 14, padding: 24 }}>
            <div style={{ display: "flex", gap: 2, marginBottom: 14, color: "#f59e0b", fontSize: 16, letterSpacing: 2 }}>★★★★★</div>
            <p style={{ fontSize: 16, lineHeight: 1.55, letterSpacing: "-.1px", margin: "0 0 18px", color: "#111" }}>"{quote}"</p>
            <div style={{ display: "flex", alignItems: "center", gap: 12, borderTop: "1px solid #ebe7e1", paddingTop: 14 }}>
              <div style={{ width: 40, height: 40, borderRadius: "50%", background: "#111", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 13, color: "#fff", flexShrink: 0 }}>
                {initials}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{name}</div>
                <div style={{ fontSize: 12.5, color: "#7b7b78" }}>{role}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
