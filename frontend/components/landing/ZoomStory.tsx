"use client";

import { useRef } from "react";
import { useScrollProgress } from "@/components/motion/hooks";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import UnitArt from "@/components/scenes/UnitArt";

const CAPTIONS = [
  { k: "01", t: "السوق مليان وحدات.", s: "مطورين كتير، وخطط سداد كل واحدة شكل، وكل إعلان بيقول «أقل مقدم»." },
  { k: "02", t: "بنقرّب على اللي يناسبك.", s: "المساعد بيسألك عن المنطقة والمقدم والقسط اللي يريحك، سؤال واحد في المرة." },
  { k: "03", t: "لحد ما توصل لوحدة على قدّك.", s: "كل وحدة معاها شارة: مناسبة، ضاغطة، أو مش مناسبة، ومعاها السبب." },
];

function TowerFacade() {
  const cols = 9;
  const rows = 15;
  return (
    <svg viewBox="0 0 400 600" className="h-[86vh] w-auto" aria-hidden>
      <defs>
        <linearGradient id="zf" x1="0" x2="1">
          <stop offset="0" stopColor="#1A1F2A" />
          <stop offset="0.5" stopColor="#262C39" />
          <stop offset="1" stopColor="#141820" />
        </linearGradient>
        <radialGradient id="zglow">
          <stop offset="0" stopColor="#C8372F" stopOpacity="0.9" />
          <stop offset="1" stopColor="#C8372F" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect x="40" y="20" width="320" height="580" fill="url(#zf)" />
      <rect x="30" y="10" width="340" height="14" fill="#2E3646" />
      {Array.from({ length: cols * rows }, (_, i) => {
        const c = i % cols;
        const r = Math.floor(i / cols);
        const x = 56 + c * 34;
        const y = 40 + r * 37;
        const target = c === 4 && r === 7;
        const lit = (c * 7 + r * 3) % 5 === 0;
        return (
          <rect
            key={i}
            x={x}
            y={y}
            width="22"
            height="24"
            rx="2"
            fill={target ? "#C8372F" : lit ? "#E9B872" : "#0E1116"}
            opacity={target ? 1 : lit ? 0.75 : 0.9}
          />
        );
      })}
      <circle cx="203" cy="311" r="40" fill="url(#zglow)" className="sun-pulse" />
    </svg>
  );
}

export default function ZoomStory() {
  const ref = useRef<HTMLElement>(null);
  useScrollProgress(ref, 3);

  return (
    <section id="how" ref={ref} className="zoom-stage relative h-[320vh] bg-ink text-paper" data-step="0">
      <div className="sticky top-0 h-screen overflow-hidden">
        {/* Zooming facade */}
        <div className="zoom-tower absolute inset-0 flex items-center justify-center">
          <TowerFacade />
        </div>

        {/* Interior: what you find inside the window */}
        <div className="zoom-interior absolute inset-0 flex items-center justify-center px-5">
          <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
            <div className="relative mx-auto w-[300px] sm:w-[330px] rounded-[38px] border-[10px] border-[#1d212b] bg-sand shadow-2xl overflow-hidden">
              <div className="bg-ink text-paper px-4 py-3 flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center font-bold text-sm">ع</div>
                <div className="text-xs font-bold">مساعد عقار</div>
              </div>
              <div className="p-3 flex flex-col gap-2 text-[12px] leading-relaxed">
                <div className="self-start bg-white rounded-2xl px-3 py-2 text-ink border border-line/40">
                  معايا مليون مقدم والقسط ميزيدش عن 50 ألف
                </div>
                <div className="self-end bg-ink text-paper rounded-2xl px-3 py-2 max-w-[85%]">
                  تمام، دي وحدة في التجمع مرتبة حسب قدرتك:
                  <div className="mt-2 bg-white text-ink rounded-xl overflow-hidden">
                    <UnitArt id="NC-101" variant="dusk" className="w-full h-24" />
                    <div className="p-2 flex items-center justify-between">
                      <span className="font-bold text-[11px]">شقة 3 غرف</span>
                      <AffordabilityBadge status="fit" />
                    </div>
                  </div>
                </div>
                <div className="self-start bg-white rounded-2xl px-3 py-2 text-ink border border-line/40">أقدر أشوفها السبت؟</div>
                <div className="self-end bg-ink text-paper rounded-2xl px-3 py-2">هوصلك بمستشار من الفريق خلال دقايق.</div>
              </div>
            </div>
            <div className="text-center md:text-right">
              <p className="text-accent font-bold text-sm">جوه الشباك</p>
              <h3 className="mt-2 text-3xl sm:text-5xl font-[900] leading-tight">محادثة واحدة بدل أيام مقارنة.</h3>
              <p className="mt-4 text-muted-dark leading-relaxed">
                الأمثلة هنا توضيحية. في الحقيقة كل رقم بييجي من الحاسبة ومن بيانات الوحدات المتراجعة.
              </p>
            </div>
          </div>
        </div>

        {/* Step captions */}
        <div className="absolute top-24 sm:top-28 right-5 sm:right-12 max-w-sm">
          {CAPTIONS.map((c, i) => (
            <div key={c.k} data-for={i} className="zoom-caption absolute top-0 right-0 w-[min(90vw,24rem)]">
              <p className="text-accent font-[900] text-sm">{c.k} / 03</p>
              <h3 className="mt-2 text-3xl sm:text-4xl font-[900] leading-tight">{c.t}</h3>
              <p className="mt-3 text-sm sm:text-base text-muted-dark leading-relaxed">{c.s}</p>
            </div>
          ))}
        </div>

        <div className="absolute bottom-8 inset-x-5 sm:inset-x-12 h-[3px] bg-paper/10 rounded-full overflow-hidden">
          <div className="zoom-bar h-full bg-accent" />
        </div>
      </div>
    </section>
  );
}
