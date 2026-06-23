"use client"

import { useState } from "react"

const FAQS = [
  ["Do I need to give you access to my Google account?", "Yes — you connect via Google OAuth, which is secure and can be revoked anytime. We never store your Google password."],
  ["How long before I see ranking improvements?", "Most businesses see movement within 3–6 weeks. Full impact is typically visible by 90 days."],
  ["Does this work for any type of business?", "Yes — restaurants, clinics, salons, agencies, retail, real estate. If you have a Google Business Profile, we can optimize it."],
  ["Can I manage multiple locations?", "Absolutely. Our Growth and Agency plans are built for multi-location businesses and marketing agencies."],
  ["Is there a free trial?", "Yes — 14 days free, no credit card required. Full access to all Starter features."],
  ["What happens if I cancel?", "Cancel anytime. Your data is yours — you can export everything before you leave."],
]

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section id="blog" style={{ maxWidth: 760, margin: "0 auto", padding: "64px 24px 0", scrollMarginTop: 80 }}>
      <div style={{ textAlign: "center", marginBottom: 36 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>FAQ</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Questions, answered
        </h2>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {FAQS.map(([q, a], i) => {
          const isOpen = open === i
          return (
            <div key={q} style={{ background: "#fff", border: `1px solid ${isOpen ? "#111" : "#d3cec6"}`, borderRadius: 8, overflow: "hidden", transition: "border-color .2s" }}>
              <button
                onClick={() => setOpen(isOpen ? null : i)}
                style={{ width: "100%", textAlign: "left", background: "none", border: "none", cursor: "pointer", padding: "20px 22px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, fontFamily: "inherit", color: "#111" }}
              >
                <span style={{ fontSize: 16, fontWeight: 600, letterSpacing: "-.2px" }}>{q}</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9c9fa5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                  style={{ flexShrink: 0, transition: "transform .3s", transform: isOpen ? "rotate(180deg)" : "rotate(0deg)", stroke: isOpen ? "#111" : "#9c9fa5" }}>
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              <div style={{ maxHeight: isOpen ? 200 : 0, overflow: "hidden", transition: "max-height .35s ease" }}>
                <p style={{ padding: "0 22px 20px", fontSize: 15, lineHeight: 1.55, color: "#626260", margin: 0 }}>{a}</p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
