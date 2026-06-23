const BRANDS = [
  { label: "SmileCare Clinics", path: "M3 21h18M5 21V7l8-4v18M19 21V11l-6-3" },
  { label: "Spice Route", path: "M3 11h18M5 11V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v6M7 21v-7M17 21v-7" },
  { label: "UrbanNest Realty", path: "M3 9 12 3l9 6v11a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z" },
  { label: "Glow Salon Co", path: "M6 3a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM6 15a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM20 4 8.12 15.88M14.47 14.48 20 20M8.12 8.12 12 12" },
  { label: "Metro Agency", path: "M2 3h6l2 4-3 2a12 12 0 0 0 6 6l2-3 4 2v6a2 2 0 0 1-2 2A18 18 0 0 1 2 5a2 2 0 0 1 0-2Z" },
]

export function SocialProofBar() {
  return (
    <section style={{ borderTop: "1px solid #ebe7e1", borderBottom: "1px solid #ebe7e1", background: "#fff" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "26px 24px", display: "flex", alignItems: "center", justifyContent: "center", gap: 18, flexWrap: "wrap" }}>
        <span style={{ fontSize: 13, color: "#9c9fa5", fontWeight: 500, marginRight: 8 }}>Powering local growth for</span>
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "center" }}>
          {BRANDS.map(({ label, path }, i) => (
            <span key={label} style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
              {i > 0 && <span style={{ color: "#d3cec6" }}>·</span>}
              <span style={{ fontSize: 15, fontWeight: 600, color: "#626260", display: "inline-flex", alignItems: "center", gap: 7 }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9c9fa5" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
                  <path d={path} />
                </svg>
                {label}
              </span>
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
