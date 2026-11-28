import SiteNav from "@/components/landing/SiteNav";
import Hero from "@/components/landing/Hero";
import AreaMarquee from "@/components/landing/AreaMarquee";
import Services from "@/components/landing/Services";
import ZoomStory from "@/components/landing/ZoomStory";
import CityCards from "@/components/landing/CityCards";
import AffordabilityShowcase from "@/components/landing/AffordabilityShowcase";
import FinalCta from "@/components/landing/FinalCta";
import SiteFooter from "@/components/landing/SiteFooter";

export default function LandingPage() {
  return (
    <div className="bg-ink">
      <SiteNav />
      <main>
        <Hero />
        <AreaMarquee />
        <Services />
        <ZoomStory />
        <CityCards />
        <AffordabilityShowcase />
        <FinalCta />
      </main>
      <SiteFooter />
    </div>
  );
}
