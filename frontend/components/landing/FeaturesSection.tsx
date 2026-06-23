"use client"

const FEATURES = [
  { title: "GBP Health Auditor", desc: "Get a full audit of your Google Business Profile in 60 seconds. See exactly what's broken and what to fix first.", path: "M12 21s7-6.16 7-12A7 7 0 0 0 5 9c0 5.84 7 12 7 12ZM12 9m-2.4 0a2.4 2.4 0 1 0 4.8 0 2.4 2.4 0 0 0-4.8 0" },
  { title: "AI Post Generator", desc: "Auto-generate keyword-rich GBP posts weekly. Scheduled, published, and tracked — without lifting a finger.", path: "M12 8V4M8 4h8M9 12h6M9 16h4", ai: true },
  { title: "Review Management", desc: "Monitor new reviews across locations in real-time. Get AI-drafted responses ready to publish in one click.", path: "m12 17.3-6.2 3.7 1.6-7L2 9.2l7.1-.6L12 2l2.9 6.6 7.1.6-5.4 4.8 1.6 7Z", ai: true },
  { title: "Rank Tracker", desc: "Track local rankings for any keyword, in any city, on a grid map. See exactly where you rank — and where you don't.", path: "M3 3v18h18M7 14l3-3 3 2 4-5" },
  { title: "Multi-Location Dashboard", desc: "Manage 1 or 100 locations from a single dashboard. Perfect for agencies and franchise businesses.", path: "M3 21h18M5 21V7l8-4v18M19 21V11l-6-3" },
  { title: "Photo & Content Optimizer", desc: "Get alerts when photos are outdated or underperforming. Upload optimized images with AI-suggested captions.", path: "M3 7h18M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7ZM9 11a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM21 15l-5-5-7 7", ai: true },
]

function FeatureCard({ title, desc, path, ai }: { title: string; desc: string; path: string; ai?: boolean }) {
  return (
    <div
      style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 12, padding: 28, transition: "border-color .25s, transform .25s" }}
      onMouseEnter={(e) => { const el = e.currentTarget; el.style.borderColor = "#111"; el.style.transform = "translateY(-3px)" }}
      onMouseLeave={(e) => { const el = e.currentTarget; el.style.borderColor = "#d3cec6"; el.style.transform = "translateY(0)" }}
    >
      <div style={{ width: 44, height: 44, borderRadius: 10, background: "#f5f1ec", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 18 }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
          <path d={path} />
        </svg>
      </div>
      <h3 style={{ fontSize: 19, fontWeight: 600, letterSpacing: "-.3px", marginBottom: 10 }}>
        {title}
        {ai && (
          <span style={{ marginLeft: 8, verticalAlign: "middle", background: "#fff2eb", color: "#ff5600", fontSize: 10.5, fontWeight: 700, letterSpacing: ".4px", padding: "3px 8px", borderRadius: 9999, border: "1px solid #ffd9c2" }}>
            AI
          </span>
        )}
      </h3>
      <p style={{ fontSize: 15, lineHeight: 1.55, color: "#626260" }}>{desc}</p>
    </div>
  )
}

export function FeaturesSection() {
  return (
    <section id="features" style={{ maxWidth: 1200, margin: "0 auto", padding: "64px 24px 0", scrollMarginTop: 80 }}>
      <div style={{ maxWidth: 680, marginBottom: 44 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>Features</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Everything your GBP needs. All in one place.
        </h2>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20 }}>
        {FEATURES.map((f) => <FeatureCard key={f.title} {...f} />)}
      </div>
    </section>
  )
}
