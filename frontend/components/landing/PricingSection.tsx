"use client"

import { useState } from "react"
import Link from "next/link"

const PLANS = [
  {
    name: "Starter", priceM: 1999, priceA: 1599, cta: "Start Free Trial", ctaHref: "/login", featured: false,
    features: ["1 GBP location", "Full profile audit", "AI post generator (4/month)", "Review monitoring", "Monthly rank report"],
  },
  {
    name: "Growth", priceM: 4999, priceA: 3999, cta: "Start Free Trial", ctaHref: "/login", featured: true,
    features: ["Up to 5 locations", "Everything in Starter", "Competitor tracking", "AI review responses", "Weekly rank reports", "WhatsApp alerts"],
  },
  {
    name: "Agency", priceM: 12999, priceA: 10399, cta: "Book a Demo", ctaHref: "/login", featured: false,
    features: ["Up to 25 locations", "Everything in Growth", "White-label reports", "Client dashboard access", "Priority support · API access"],
  },
]

function CheckIcon({ color = "#0bdf50" }: { color?: string }) {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
      <path d="M20 6 9 17l-5-5" />
    </svg>
  )
}

export function PricingSection() {
  const [annual, setAnnual] = useState(false)

  return (
    <section id="pricing" className="landing-section" style={{ scrollMarginTop: 80 }}>
      <div style={{ textAlign: "center", maxWidth: 620, margin: "0 auto 40px" }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>Pricing</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          Simple pricing. No surprises.
        </h2>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 4, background: "#ebe7e1", borderRadius: 9999, padding: 4, marginTop: 28 }}>
          {[{ label: "Monthly", val: false }, { label: "Annual", val: true }].map(({ label, val }) => (
            <button key={label} onClick={() => setAnnual(val)}
              style={{ background: annual === val ? "#fff" : "transparent", color: annual === val ? "#111" : "#626260", fontSize: 14, fontWeight: 600, padding: "9px 20px", borderRadius: 9999, border: "none", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 7, transition: "background .2s, color .2s" }}
            >
              {label}
              {val && <span style={{ background: "#0bdf50", color: "#063d18", fontSize: 11, fontWeight: 700, padding: "2px 7px", borderRadius: 9999 }}>−20%</span>}
            </button>
          ))}
        </div>
      </div>

      <div className="landing-three-col" style={{ alignItems: "start" }}>
        {PLANS.map(({ name, priceM, priceA, cta, ctaHref, featured, features }) => {
          const price = annual ? priceA : priceM
          return (
            <div key={name} style={{ background: featured ? "#111" : "#fff", color: featured ? "#fff" : "#111", border: `1px solid ${featured ? "#111" : "#d3cec6"}`, borderRadius: 12, padding: 30, position: "relative" }}>
              {featured && (
                <div style={{ position: "absolute", top: -12, left: 30, background: "#0bdf50", color: "#063d18", fontSize: 12, fontWeight: 700, padding: "4px 12px", borderRadius: 9999 }}>
                  Most popular
                </div>
              )}
              <div style={{ fontSize: 14, fontWeight: 600, color: featured ? "#9c9fa5" : "#626260" }}>{name}</div>
              <div style={{ margin: "14px 0 4px", display: "flex", alignItems: "baseline", gap: 4 }}>
                <span style={{ fontSize: 18, fontWeight: 600, color: featured ? "#9c9fa5" : "#626260" }}>₹</span>
                <span style={{ fontSize: 42, fontWeight: 600, letterSpacing: "-1.6px" }}>{price.toLocaleString("en-IN")}</span>
                <span style={{ fontSize: 15, color: featured ? "#9c9fa5" : "#7b7b78" }}>/mo</span>
              </div>
              <div style={{ fontSize: 13, color: "#9c9fa5", height: 18, marginBottom: 4 }}>
                {annual ? "billed annually · save 20%" : ""}
              </div>
              <Link href={ctaHref}
                style={{ display: "block", textAlign: "center", background: featured ? "#fff" : "transparent", color: featured ? "#111" : "#111", border: `1px solid ${featured ? "transparent" : "#111"}`, fontSize: 15, fontWeight: featured ? 600 : 500, padding: 12, borderRadius: 8, margin: "22px 0", textDecoration: "none" }}
              >
                {cta}
              </Link>
              <div style={{ display: "flex", flexDirection: "column", gap: 12, fontSize: 14.5, color: featured ? "#e6e6e4" : "#3a3a38" }}>
                {features.map((f) => (
                  <div key={f} style={{ display: "flex", gap: 10 }}>
                    <CheckIcon color="#0bdf50" />
                    {f}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
