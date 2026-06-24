"use client"

const PROBLEMS = [
  {
    title: "You're not showing up",
    desc: "\"Near me\" searches are exploding. But if your GBP isn't optimized, Google shows your competitor — every single time.",
    icon: "M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0ZM12 10m-1 0a1 1 0 1 0 2 0 1 1 0 0 0-2 0",
    stat: "76%",
    statLabel: "of local searches lead to a store visit within 24h",
    accent: "#ff5600",
    accentBg: "#fff5f0",
  },
  {
    title: "Reviews are slipping through",
    desc: "You get a bad review. No one responds. Google notices. Your ranking drops. Most businesses don't even know it's happening.",
    icon: "m12 17.3-6.2 3.7 1.6-7L2 9.2l7.1-.6L12 2l2.9 6.6 7.1.6-5.4 4.8 1.6 7Z",
    stat: "88%",
    statLabel: "of consumers read reviews before choosing a local business",
    accent: "#c41c1c",
    accentBg: "#fff0f0",
  },
  {
    title: "No idea what's working",
    desc: "You updated your hours once and hoped for the best. There's zero visibility into what's driving — or killing — your local rankings.",
    icon: "M3 3v18h18M7 15l3-4 3 2 4-6",
    stat: "60%",
    statLabel: "of GBP profiles have critical errors hurting their ranking",
    accent: "#7c3aed",
    accentBg: "#f5f0ff",
  },
]

export function ProblemSection() {
  return (
    <section className="landing-section">
      <div style={{ maxWidth: 680, marginBottom: 44 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>The problem</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600, margin: 0 }}>
          Why most local businesses are invisible on Google
        </h2>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {PROBLEMS.map(({ title, desc, icon, stat, statLabel, accent, accentBg }) => (
          <div key={title}
            style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 14, overflow: "hidden", display: "flex" }}
          >
            {/* Accent left bar */}
            <div style={{ width: 4, flexShrink: 0, background: accent }} />

            <div style={{ flex: 1, padding: "24px 24px 24px 22px" }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                {/* Icon */}
                <div style={{ width: 44, height: 44, borderRadius: 10, background: accentBg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={accent} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d={icon} />
                  </svg>
                </div>

                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-.3px", margin: "0 0 8px" }}>{title}</h3>
                  <p style={{ fontSize: 14.5, lineHeight: 1.6, color: "#626260", margin: "0 0 16px" }}>{desc}</p>

                  {/* Inline stat */}
                  <div style={{ display: "inline-flex", alignItems: "center", gap: 10, background: accentBg, border: `1px solid ${accent}22`, borderRadius: 10, padding: "8px 14px" }}>
                    <span style={{ fontSize: 22, fontWeight: 700, color: accent, letterSpacing: "-1px", lineHeight: 1 }}>{stat}</span>
                    <span style={{ fontSize: 12.5, color: "#626260", lineHeight: 1.4 }}>{statLabel}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
