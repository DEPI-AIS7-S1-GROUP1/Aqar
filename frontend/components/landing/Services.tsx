"use client";

import { useRef, type ReactNode } from "react";
import Reveal from "@/components/motion/Reveal";
import { useSpotlight } from "@/components/motion/hooks";

const ICONS: Record<string, ReactNode> = {
  chat: <path d="M4 5h16v11H9l-5 4V5z M8 9h8 M8 12h5" />,
  wallet: <path d="M3 7h15a3 3 0 013 3v7a3 3 0 01-3 3H3V7z M3 7l12-4v4 M16 14h2" />,
  compare: <path d="M4 20V9 M10 20V4 M16 20v-8 M22 20H2" />,
  handshake: <path d="M2 12l5-5 4 3 3-3 5 5-6 6-3-3-3 3-5-6z M11 10l4 4" />,
};

const SERVICES = [
  { icon: "chat", title: "شات بالعامية", body: "اكتب زي ما بتتكلم: «معايا مليون مقدم وعايز قسط على قدي». المساعد يفهمك ويسألك سؤال واحد في المرة." },
  { icon: "wallet", title: "وحدات تقدر عليها", body: "مش بس اللي في ميزانيتك: بنحسب المقدم والقسط ودفعة الاستلام لكل وحدة ونقولك مناسبة ولا ضاغطة ولا لأ." },
  { icon: "compare", title: "مقارنة خطط السداد", body: "خطتين جنب بعض: المقدم، القسط، دفعة الاستلام، الإجمالي والقيمة الحالية. كل رقم من الحاسبة، مش من تخمين." },
  { icon: "handshake", title: "وسيط معاه ملفك", body: "لما تحب تعاين أو تحجز، بنوصلك بوسيط عنده ملخص كامل لطلبك، فمش هتعيد الكلام من الأول." },
];

function Card({ s, i }: { s: (typeof SERVICES)[number]; i: number }) {
  const ref = useRef<HTMLDivElement>(null);
  useSpotlight(ref);
  return (
    <Reveal delay={i * 120} className="h-full">
      <div
        ref={ref}
        className="spotlight group h-full rounded-[24px] border border-paper/10 bg-paper/[0.03] p-7 transition-all duration-500 hover:-translate-y-2 hover:border-accent/40"
      >
        <div className="w-14 h-14 rounded-2xl bg-accent/15 text-accent flex items-center justify-center transition-transform duration-500 group-hover:rotate-[-8deg] group-hover:scale-110">
          <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            {ICONS[s.icon]}
          </svg>
        </div>
        <p className="mt-8 text-xs font-bold text-muted-dark">0{i + 1}</p>
        <h3 className="mt-1 text-xl font-[900] text-paper">{s.title}</h3>
        <p className="mt-3 text-sm leading-relaxed text-muted-dark">{s.body}</p>
      </div>
    </Reveal>
  );
}

export default function Services() {
  return (
    <section id="services" className="relative bg-ink text-paper py-24 sm:py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
          <Reveal>
            <p className="text-accent font-bold text-sm">خدماتنا</p>
            <h2 className="mt-3 text-4xl sm:text-6xl font-[900] tracking-tight leading-tight">
              مش بنبيعلك حلم.
              <br />
              <span className="text-muted-dark">بنوريك اللي تقدر عليه.</span>
            </h2>
          </Reveal>
          <Reveal delay={150} className="max-w-md text-muted-dark leading-relaxed">
            أغلب المواقع بتسألك عن الميزانية وخلاص. إحنا بنشوف المقدم والقسط ودفعة الاستلام لكل
            وحدة، عشان ماتتفاجئش بعدين.
          </Reveal>
        </div>

        <div className="mt-14 grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {SERVICES.map((s, i) => (
            <Card key={s.title} s={s} i={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
