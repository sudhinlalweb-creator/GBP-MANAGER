"use client"

const PROBLEMS = [
  {
    title: "You're not showing up",
    desc: "\"Near me\" searches are exploding. But if your GBP isn't optimized, Google shows your competitor — every single time.",
    path: "M10.5 10.5a4 4 0 1 0 3 3M21 21l-4.35-4.35",
  },
  {
    title: "Reviews are slipping through",
    desc: "You get a bad review. No one responds. Google notices. Your ranking drops. Most businesses don't even know it's happening.",
    path: "m12 17.3-6.2 3.7 1.6-7L2 9.2l7.1-.6L12 2l2.9 6.6 7.1.6-5.4 4.8 1.6 7Z",
  },
  {
    title: "No idea what's working",
    desc: "You updated your hours once and hoped for the best. There's zero visibility into what's driving — or killing — your local rankings.",
    path: "M3 3v18h18M7 15l3-4 3 2 4-6",
  },
]

function ProblemCard({ title, desc, path, delay }: { title: string; desc: string; path: string; delay: number }) {
  return (
    <div
      style={{
        background: "#fff", border: "1px solid #d3cec6", borderRadius: 12, padding: 28,
        transition: "border-color .25s, transform .25s",
      }}
      onMouseEnter={(e) => { const el = e.currentTarget; el.style.borderColor = "#111"; el.style.transform = "translateY(-3px)" }}
      onMouseLeave={(e) => { const el = e.currentTarget; el.style.borderColor = "#d3cec6"; el.style.transform = "translateY(0)" }}
    >
      <div style={{ width: 42, height: 42, borderRadius: 10, background: "#f5f1ec", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 18 }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
          <path d={path} />
        </svg>
      </div>
      <h3 style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-.3px", marginBottom: 10 }}>{title}</h3>
      <p style={{ fontSize: 15, lineHeight: 1.55, color: "#626260" }}>{desc}</p>
    </div>
  )
}

export function ProblemSection() {
  return (
    <section style={{ maxWidth: 1200, margin: "0 auto", padding: "64px 24px 0" }}>
      <div style={{ maxWidth: 680, marginBottom: 44 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>The problem</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Why most local businesses are invisible on Google
        </h2>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20 }}>
        {PROBLEMS.map((p, i) => <ProblemCard key={p.title} {...p} delay={i * 0.08} />)}
      </div>
    </section>
  )
}
