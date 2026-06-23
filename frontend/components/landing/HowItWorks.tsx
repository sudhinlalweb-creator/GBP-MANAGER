const STEPS = [
  { n: 1, title: "Connect", desc: "Link your Google Business Profile in one click. No technical setup. No developer needed." },
  { n: 2, title: "Audit", desc: "We scan your entire profile and give you a score with a prioritized fix list. You'll know exactly where you stand." },
  { n: 3, title: "Optimize", desc: "Apply AI recommendations, schedule posts, respond to reviews, and watch your ranking climb." },
  { n: 4, title: "Monitor", desc: "Get weekly ranking reports, review alerts, and competitor tracking delivered to your inbox automatically." },
]

export function HowItWorks() {
  return (
    <section id="how" className="landing-section" style={{ scrollMarginTop: 80 }}>
      <div style={{ maxWidth: 680, marginBottom: 48 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>How it works</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Up and running in 3 minutes
        </h2>
      </div>
      <div style={{ position: "relative" }}>
        {/* connector line */}
        <div className="landing-step-line" style={{ position: "absolute", top: 23, left: "8%", right: "8%", height: 1, background: "#d3cec6" }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 24, position: "relative" }}>
          {STEPS.map(({ n, title, desc }) => (
            <div key={n}>
              <div style={{ width: 46, height: 46, borderRadius: "50%", background: "#111", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 600, fontSize: 17, position: "relative", zIndex: 1 }}>
                {n}
              </div>
              <h3 style={{ fontSize: 19, fontWeight: 600, letterSpacing: "-.3px", margin: "18px 0 9px" }}>{title}</h3>
              <p style={{ fontSize: 14.5, lineHeight: 1.55, color: "#626260" }}>{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
