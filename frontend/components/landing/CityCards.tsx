import Link from "next/link";
import type { ReactNode } from "react";
import Reveal from "@/components/motion/Reveal";
import { MiniCairo } from "@/components/scenes/CairoScene";
import { MiniCapital, MiniCoast, MiniPyramids } from "@/components/scenes/MiniScenes";

const CITIES: { area: string; name: string; tag: string; blurb: string; scene: ReactNode }[] = [
  { area: "new_cairo", name: "القاهرة الجديدة", tag: "شرق القاهرة", blurb: "كمبوندات التجمع وقربها من الجامعات والمحاور.", scene: <MiniCairo /> },
  { area: "sheikh_zayed", name: "زايد وأكتوبر", tag: "غرب القاهرة", blurb: "على مرمى حجر من الأهرامات والمتحف المصري الكبير.", scene: <MiniPyramids /> },
  { area: "new_capital", name: "العاصمة الإدارية", tag: "العاصمة الجديدة", blurb: "حي الأعمال والبرج الأيقوني وأحياء سكنية جديدة.", scene: <MiniCapital /> },
  { area: "north_coast_ras_el_hekma", name: "الساحل الشمالي", tag: "البحر المتوسط", blurb: "شاليهات على البحر من العلمين لرأس الحكمة.", scene: <MiniCoast /> },
];

export default function CityCards() {
  return (
    <section id="cities" className="bg-paper text-ink py-24 sm:py-32">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <Reveal className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <p className="text-accent font-bold text-sm">المناطق</p>
            <h2 className="mt-3 text-4xl sm:text-6xl font-[900] tracking-tight">من النيل للمتوسط.</h2>
          </div>
          <p className="max-w-sm text-muted leading-relaxed">اختار منطقة وشوف الوحدات المتاحة فيها، أو سيب المساعد يرشحلك.</p>
        </Reveal>

        <div className="city-row mt-12 flex flex-col lg:flex-row gap-4 lg:h-[520px]">
          {CITIES.map((c, i) => (
            <div key={c.area} className="city-card min-h-[340px] lg:min-h-0">
            <Reveal delay={i * 110} variant="scale" className="h-full">
              <Link
                href={`/listings?area=${c.area}`}
                className="group relative block h-full rounded-[28px] overflow-hidden text-paper focus:outline-none focus-visible:ring-4 focus-visible:ring-accent/50"
              >
                <div className="absolute inset-0 transition-transform duration-[1.2s] group-hover:scale-105">{c.scene}</div>
                <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/30 to-transparent" />
                <div className="absolute top-5 right-5 rounded-full bg-ink/50 backdrop-blur px-3 py-1 text-xs font-bold">{c.tag}</div>
                <div className="absolute bottom-0 inset-x-0 p-6">
                  <h3 className="text-2xl sm:text-3xl font-[900]">{c.name}</h3>
                  <div className="city-more">
                    <p className="mt-2 text-sm text-paper/80 leading-relaxed max-w-xs">{c.blurb}</p>
                    <span className="mt-4 inline-flex items-center gap-2 rounded-full bg-paper text-ink px-4 py-2 text-sm font-bold">
                      شوف الوحدات
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden>
                        <path d="M19 12H5M11 18l-6-6 6-6" />
                      </svg>
                    </span>
                  </div>
                </div>
              </Link>
            </Reveal>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
