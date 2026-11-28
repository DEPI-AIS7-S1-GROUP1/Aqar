import Link from "next/link";
import Reveal from "@/components/motion/Reveal";
import { AlexandriaNight } from "@/components/scenes/MiniScenes";
import RotatingRing from "./RotatingRing";

export default function FinalCta() {
  return (
    <section className="relative bg-ink text-paper overflow-hidden">
      <div className="absolute inset-0 opacity-70">
        <AlexandriaNight />
      </div>
      <div className="absolute inset-0 bg-gradient-to-l from-ink via-ink/60 to-ink/20" />
      <div className="relative max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 py-28 sm:py-40 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-10">
        <Reveal>
          <h2 className="text-4xl sm:text-6xl font-[900] tracking-tight leading-tight">
            بيتك الجاي
            <br />
            <span className="text-gold">على قدّك.</span>
          </h2>
          <p className="mt-5 text-muted-dark max-w-md leading-relaxed">
            اعمل حساب في دقيقة، واحكي للمساعد بتدور على إيه. مش هنطلب منك غير اللي محتاجينه.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/signup" className="bg-accent px-8 py-4 rounded-full font-bold shadow-xl shadow-accent/30 hover:-translate-y-[2px] transition-transform">
              إنشاء حساب
            </Link>
            <Link href="/login" className="border border-paper/30 px-8 py-4 rounded-full font-bold hover:border-paper transition-colors">
              تسجيل الدخول
            </Link>
          </div>
        </Reveal>
        <Reveal variant="scale" delay={200}>
          <RotatingRing text="القاهرة ● الإسكندرية ● الساحل ● العاصمة ● " />
        </Reveal>
      </div>
    </section>
  );
}
