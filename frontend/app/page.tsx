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
    <div style={{ background: "#f5f1ec", color: "#111", overflowX: "hidden", minHeight: "100vh", fontFamily: "'Inter', ui-sans-serif, system-ui" }}>
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
    </div>
  )
}
