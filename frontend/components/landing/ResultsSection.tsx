"use client"

import { useEffect, useRef } from "react"

const STATS = [
  { count: 2400, suffix: "+", label: "Businesses optimized" },
  { count: 41, suffix: "%", label: "Average ranking improvement in 90 days", green: true },
  { count: 3.2, suffix: "x", label: "More profile views after optimization", decimals: 1 },
  { count: 98, suffix: "%", label: "Customer satisfaction score" },
]

const TESTIMONIALS = [
  { quote: "\"We went from page 3 to the top 3 in our city within 6 weeks. Our walk-ins increased by 40%.\"", initials: "RM", name: "Rohan M.", role: "Restaurant Owner, Bangalore" },
  { quote: "\"Managing 12 clinic locations used to take hours every week. Now it's one dashboard, 20 minutes.\"", initials: "PS", name: "Dr. Priya S.", role: "Multi-location Clinic, Mumbai" },
  { quote: "\"The AI post scheduler alone saved us 8 hours a month. The ranking gains were a bonus.\"", initials: "AK", name: "Amit K.", role: "Digital Marketing Agency, Delhi" },
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
        const dur = 1500
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
    }, { threshold: 0.1 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [count, suffix, decimals])

  return (
    <div style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 12, padding: 26 }}>
      <div style={{ fontSize: 44, fontWeight: 600, letterSpacing: "-1.8px", lineHeight: 1, color: green ? "#0bdf50" : "#111" }}>
        <span ref={spanRef}>0{suffix}</span>
      </div>
      <div style={{ fontSize: 14.5, color: "#626260", marginTop: 8, lineHeight: 1.4 }}>{label}</div>
    </div>
  )
}

export function ResultsSection() {
  return (
    <section id="agencies" style={{ maxWidth: 1200, margin: "0 auto", padding: "64px 24px 0", scrollMarginTop: 80 }}>
      <div style={{ maxWidth: 680, marginBottom: 44 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>Results</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Real businesses. Real results.
        </h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 20 }}>
        {STATS.map((s) => <StatCard key={s.label} {...s} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20, marginTop: 20 }}>
        {TESTIMONIALS.map(({ quote, initials, name, role }) => (
          <div key={name} style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 12, padding: 30 }}>
            <div style={{ display: "flex", gap: 3, marginBottom: 16, color: "#f59e0b", fontSize: 18 }}>★★★★★</div>
            <p style={{ fontSize: 17, lineHeight: 1.5, letterSpacing: "-.1px", marginBottom: 20 }}>{quote}</p>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 42, height: 42, borderRadius: "50%", background: "#ebe7e1", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 600, fontSize: 15, color: "#626260" }}>
                {initials}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{name}</div>
                <div style={{ fontSize: 13, color: "#7b7b78" }}>{role}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
