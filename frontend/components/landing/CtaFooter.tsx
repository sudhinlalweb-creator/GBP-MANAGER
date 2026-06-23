"use client"

import Link from "next/link"

const LINKS = ["Features", "Pricing", "Blog", "About", "Contact", "Privacy", "Terms"]

export function CtaFooter() {
  return (
    <>
      {/* Final CTA */}
      <section className="landing-section" style={{ paddingTop: 96, paddingBottom: 32 }}>
        <div style={{ background: "#111", color: "#fff", borderRadius: 24, padding: "72px 32px", textAlign: "center", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, background: "radial-gradient(600px 300px at 50% -10%, rgba(255,86,0,.18), transparent 70%)", pointerEvents: "none" }} />
          <div style={{ position: "relative" }}>
            <h2 style={{ fontSize: "clamp(28px,4vw,46px)", lineHeight: 1.08, letterSpacing: "-1.5px", fontWeight: 600, maxWidth: 760, margin: "0 auto" }}>
              Your next customer is already searching on Google.
            </h2>
            <p style={{ fontSize: 20, color: "#9c9fa5", marginTop: 18 }}>
              Will they find you — or your competitor?
            </p>
            <Link href="/login"
              style={{ display: "inline-flex", alignItems: "center", gap: 9, background: "#fff", color: "#111", fontSize: 16, fontWeight: 600, padding: "15px 28px", borderRadius: 8, marginTop: 32, textDecoration: "none" }}
            >
              Start your free 14-day trial
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </Link>
            <div style={{ fontSize: 13.5, color: "#7b7b78", marginTop: 18 }}>
              No credit card required · Setup in 3 minutes · Cancel anytime
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid #ebe7e1" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "56px 24px 40px" }}>
          <div className="landing-footer-grid">
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 9, fontWeight: 600, fontSize: 19, letterSpacing: "-.4px", marginBottom: 12 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                  <path d="M12 22s7-6.16 7-12A7 7 0 0 0 5 10c0 5.84 7 12 7 12Z" fill="#111" />
                  <circle cx="12" cy="10" r="2.6" fill="#fff" />
                </svg>
                Pinly
              </div>
              <p style={{ fontSize: 14.5, color: "#7b7b78", maxWidth: 340, lineHeight: 1.5 }}>
                AI-powered Google Business Profile management that gets local businesses to the top of search — and keeps them there.
              </p>
            </div>
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap", fontSize: 14, color: "#626260" }}>
              {LINKS.map((link) => (
                <a key={link} href="#"
                  style={{ color: "#626260", textDecoration: "none", transition: "color .2s" }}
                  onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "#111" }}
                  onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "#626260" }}
                >
                  {link}
                </a>
              ))}
            </div>
          </div>
          <div style={{ borderTop: "1px solid #ebe7e1", marginTop: 36, paddingTop: 22, display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12, fontSize: 13, color: "#9c9fa5" }}>
            <span>Made in India 🇮🇳 for local businesses worldwide</span>
            <span>© 2025 Pinly. All rights reserved.</span>
          </div>
        </div>
      </footer>
    </>
  )
}
