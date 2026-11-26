"use client";

import Link from "next/link";
import { useRef, type CSSProperties } from "react";
import { useParallax } from "@/components/motion/hooks";
import {
  CitadelLayer,
  NileLayer,
  PyramidsLayer,
  RiversideLayer,
  SkyLayer,
  TowersLayer,
} from "@/components/scenes/CairoScene";
import RotatingRing from "./RotatingRing";

const layer = (d: number, ds: number): CSSProperties =>
  ({ "--d": d, "--ds": ds } as CSSProperties);

const LINES = ["يفهم العميل.", "يتأكد إنه يقدر يدفع.", "يسلّمه للوسيط جاهز."];

export default function Hero() {
  const ref = useRef<HTMLElement>(null);
  useParallax(ref);

  return (
    <section ref={ref} className="relative min-h-[100svh] overflow-hidden bg-ink text-paper select-none">
      {/* Cairo at dusk, 6 parallax layers (far layers move least) */}
      <div className="absolute inset-0">
        <div className="plx absolute inset-0" style={layer(4, 0.1)}><SkyLayer /></div>
        <div className="plx absolute inset-0" style={layer(10, 0.18)}><PyramidsLayer /></div>
        <div className="plx absolute inset-0" style={layer(16, 0.26)}><CitadelLayer /></div>
        <div className="plx absolute inset-0" style={layer(24, 0.34)}><TowersLayer /></div>
        <div className="plx absolute inset-[-2%]" style={layer(34, 0.42)}><RiversideLayer /></div>
        <div className="plx absolute inset-[-2%]" style={layer(44, 0.5)}><NileLayer /></div>
      </div>

      {/* readability: darken the text side (right in RTL) and the top */}
      <div className="absolute inset-0 bg-gradient-to-l from-ink/95 via-ink/45 to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(60%_55%_at_80%_35%,rgba(14,17,22,0.75),transparent_70%)]" />
      <div className="absolute inset-x-0 top-0 h-48 bg-gradient-to-b from-ink to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-ink to-transparent" />

      {/* giant faint word */}
      <div
        aria-hidden
        className="pointer-events-none absolute top-16 right-[-4%] text-[160px] sm:text-[280px] lg:text-[420px] font-[900] text-paper/[0.05] leading-none"
      >
        عقار
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 pt-36 sm:pt-44 pb-24 min-h-[100svh] flex flex-col">
        <p className="fade-in inline-flex items-center gap-2 self-start rounded-full border border-paper/15 bg-ink/40 backdrop-blur px-4 py-1.5 text-xs sm:text-sm text-muted-dark" style={{ animationDelay: "0.1s" }}>
          <span className="w-1.5 h-1.5 rounded-full bg-accent pulse-ring" />
          مساعد مبيعات عقاري بالعامية المصرية
        </p>

        <h1 className="mt-6 text-[38px] sm:text-6xl lg:text-[76px] font-[900] leading-[1.15] tracking-tight max-w-4xl">
          {LINES.map((l, i) => (
            <span key={l} className="rise-line">
              <span style={{ animationDelay: `${0.25 + i * 0.18}s` }} className={i === 1 ? "text-gold" : undefined}>
                {l}
              </span>
            </span>
          ))}
        </h1>

        <p className="fade-in mt-6 text-base sm:text-lg text-muted-dark max-w-2xl leading-relaxed" style={{ animationDelay: "0.9s" }}>
          من التجمع لزايد للعاصمة للساحل: احكي للمساعد بتدور على إيه ومعاك مقدم قد إيه، وهو يرشحلك
          وحدات تقدر تدفعها فعلاً، ويقارنلك خطط السداد، ولما تبقى جاهز يوصلك بوسيط معاه ملفك كامل.
        </p>

        <div className="fade-in mt-9 flex flex-wrap items-center gap-4" style={{ animationDelay: "1.1s" }}>
          <Link
            href="/signup"
            className="group bg-accent text-paper font-bold px-8 py-4 rounded-full shadow-xl shadow-accent/30 hover:-translate-y-[2px] transition-transform inline-flex items-center gap-3"
          >
            ابدأ مع المساعد
            <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden>
              <path d="M19 12H5M11 18l-6-6 6-6" />
            </svg>
          </Link>
          <Link
            href="/listings"
            className="border border-paper/30 bg-ink/30 backdrop-blur font-bold px-8 py-4 rounded-full hover:border-paper hover:-translate-y-[2px] transition-all"
          >
            تصفح الوحدات
          </Link>
          <Link href="/login" className="text-sm font-bold text-muted-dark hover:text-paper underline-offset-4 hover:underline">
            عندي حساب
          </Link>
        </div>

        <div className="mt-auto pt-16 flex items-end justify-between gap-6">
          <a
            href="#services"
            aria-label="انزل لخدماتنا"
            className="w-12 h-12 rounded-full bg-accent flex items-center justify-center shadow-lg animate-scroll-bob"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </a>
          <div className="hidden lg:block">
            <RotatingRing />
          </div>
        </div>
      </div>
    </section>
  );
}
