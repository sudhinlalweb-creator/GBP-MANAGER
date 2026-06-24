import Link from "next/link"
import { LandingNav } from "@/components/landing/LandingNav"
import { HeroSection } from "@/components/landing/HeroSection"
import { SocialProofBar } from "@/components/landing/SocialProofBar"
import { ProblemSection } from "@/components/landing/ProblemSection"
import { FeaturesSection } from "@/components/landing/FeaturesSection"
import { HowItWorks } from "@/components/landing/HowItWorks"
import { RankTracker } from "@/components/landing/RankTracker"
import { ResultsSection } from "@/components/landing/ResultsSection"
import { PricingSection } from "@/components/landing/PricingSection"
import { FaqSection } from "@/components/landing/FaqSection"
import { CtaFooter } from "@/components/landing/CtaFooter"

export default function HomePage() {
  return (
    <div className="landing-page-wrapper" style={{ background: "#f5f1ec", color: "#111", overflowX: "hidden", minHeight: "100vh", fontFamily: "'Inter', ui-sans-serif, system-ui" }}>
      <LandingNav />
      <span id="top" />
      <HeroSection />
      <SocialProofBar />
      <ProblemSection />
      <FeaturesSection />
      <HowItWorks />
      <RankTracker />
      <ResultsSection />
      <PricingSection />
      <FaqSection />
      <CtaFooter />

      {/* Sticky mobile CTA */}
      <div className="landing-sticky-cta">
        <Link href="/login"
          style={{ flex: 1, background: "#111", color: "#fff", fontSize: 15, fontWeight: 600, padding: "14px", borderRadius: 10, textDecoration: "none", textAlign: "center", display: "block" }}>
          Start Free — 14 Days
        </Link>
        <Link href="/login"
          style={{ flexShrink: 0, background: "#fff", color: "#111", fontSize: 14, fontWeight: 500, padding: "14px 18px", borderRadius: 10, textDecoration: "none", border: "1px solid #d3cec6", display: "block" }}>
          Log in
        </Link>
      </div>
    </div>
  )
}
