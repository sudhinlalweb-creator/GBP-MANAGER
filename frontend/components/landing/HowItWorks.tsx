"use client"

const STEPS = [
  {
    n: 1,
    title: "Connect",
    desc: "Link your Google Business Profile in one click. No technical setup. No developer needed.",
    time: "~30 sec",
    icon: "M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9ZM13 2v7h7M9 13h6M9 17h4",
  },
  {
    n: 2,
    title: "Audit",
    desc: "We scan your entire profile and give you a score with a prioritized fix list. You'll know exactly where you stand.",
    time: "~60 sec",
    icon: "M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11",
  },
  {
    n: 3,
    title: "Optimize",
    desc: "Apply AI recommendations, schedule posts, respond to reviews, and watch your ranking climb.",
    time: "~1 min",
    icon: "M13 10V3L4 14h7v7l9-11h-7",
  },
  {
    n: 4,
    title: "Monitor",
    desc: "Get weekly ranking reports, review alerts, and competitor tracking delivered automatically.",
    time: "Ongoing",
    icon: "M3 3v18h18M7 14l3-3 3 2 4-5",
  },
]

export function HowItWorks() {
  return (
    <section id="how" className="landing-section" style={{ scrollMarginTop: 80 }}>
      <div style={{ maxWidth: 680, marginBottom: 48 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>How it works</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600, margin: 0 }}>
          Up and running in 3 minutes
        </h2>
      </div>

      {/* Desktop: horizontal stepper */}
      <div className="how-desktop" style={{ position: "relative" }}>
        <div style={{ position: "absolute", top: 23, left: "6%", right: "6%", height: 1, background: "linear-gradient(90deg, #d3cec6 0%, #111 50%, #d3cec6 100%)", opacity: .35 }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24, position: "relative" }}>
          {STEPS.map(({ n, title, desc, time, icon }) => (
            <div key={n}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
                <div style={{ width: 46, height: 46, borderRadius: "50%", background: "#111", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 16, flexShrink: 0, position: "relative", zIndex: 1 }}>
                  {n}
                </div>
                <span style={{ fontSize: 12, fontWeight: 600, color: "#9c9fa5", letterSpacing: ".3px", background: "#ebe7e1", borderRadius: 9999, padding: "3px 10px" }}>{time}</span>
              </div>
              <h3 style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-.3px", margin: "0 0 8px" }}>{title}</h3>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: "#626260", margin: 0 }}>{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile: vertical timeline */}
      <div className="how-mobile" style={{ display: "none", flexDirection: "column", position: "relative" }}>
        <div style={{ position: "absolute", left: 22, top: 24, bottom: 24, width: 1, background: "linear-gradient(180deg, #111 0%, #d3cec6 100%)", opacity: .3 }} />
        {STEPS.map(({ n, title, desc, time, icon }, i) => (
          <div key={n} style={{ display: "flex", gap: 20, paddingBottom: i < STEPS.length - 1 ? 32 : 0 }}>
            <div style={{ flexShrink: 0, width: 46, height: 46, borderRadius: "50%", background: "#111", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 16, position: "relative", zIndex: 1 }}>
              {n}
            </div>
            <div style={{ paddingTop: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                <h3 style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-.3px", margin: 0 }}>{title}</h3>
                <span style={{ fontSize: 11, fontWeight: 600, color: "#9c9fa5", background: "#ebe7e1", borderRadius: 9999, padding: "2px 8px", flexShrink: 0 }}>{time}</span>
              </div>
              <p style={{ fontSize: 14.5, lineHeight: 1.6, color: "#626260", margin: 0 }}>{desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
