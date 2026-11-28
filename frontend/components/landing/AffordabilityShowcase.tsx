"use client";

import { useMemo, useState } from "react";
import Reveal from "@/components/motion/Reveal";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import UnitArt from "@/components/scenes/UnitArt";
import { LISTINGS } from "@/lib/mock/db";
import { buildPlan, checkAffordability } from "@/lib/mock/finance";
import { formatEgp } from "@/lib/format";

// Illustrative example on one demo unit, computed with the demo calculator.
const PERSONAS = [
  { id: "a", label: "مقدم مليون · قسط 50 ألف", down: 1_000_000, monthly: 50_000 },
  { id: "b", label: "مقدم 500 ألف · قسط 45 ألف", down: 500_000, monthly: 45_000 },
  { id: "c", label: "مقدم 300 ألف · قسط 20 ألف", down: 300_000, monthly: 20_000 },
];

export default function AffordabilityShowcase() {
  const [pid, setPid] = useState("b");
  const listing = LISTINGS[0];
  const plan = useMemo(() => buildPlan(listing), [listing]);
  const persona = PERSONAS.find((p) => p.id === pid)!;
  const aff = checkAffordability(plan, persona.down, persona.monthly);

  return (
    <section className="bg-sand text-ink py-24 sm:py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 grid lg:grid-cols-2 gap-12 items-center">
        <Reveal>
          <p className="text-accent font-bold text-sm">اللي بيفرّقنا</p>
          <h2 className="mt-3 text-4xl sm:text-5xl font-[900] tracking-tight leading-tight">
            نفس الوحدة.
            <br />
            تلات عملاء.
            <br />
            <span className="text-accent">تلات إجابات مختلفة.</span>
          </h2>
          <p className="mt-6 text-muted leading-relaxed max-w-lg">
            الميزانية لوحدها مش كفاية. دفعة الاستلام ممكن توقف عميل متحمس. اختار عميل وشوف الشارة
            بتتغير إزاي.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row lg:flex-col xl:flex-row gap-3" role="radiogroup" aria-label="اختار عميل">
            {PERSONAS.map((p) => (
              <button
                key={p.id}
                type="button"
                role="radio"
                aria-checked={pid === p.id}
                onClick={() => setPid(p.id)}
                className={`rounded-full px-5 py-3 text-sm font-bold border transition-all duration-300 ${
                  pid === p.id
                    ? "bg-ink text-paper border-ink shadow-lg -translate-y-[2px]"
                    : "bg-white text-ink border-line hover:border-ink"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </Reveal>

        <Reveal variant="scale" delay={120}>
          <div className="relative rounded-[28px] bg-white shadow-2xl shadow-ink/10 overflow-hidden border border-line/50">
            <div className="relative">
              <UnitArt id={listing.listing_id} variant="day" className="w-full h-56 sm:h-64" />
              <span className="absolute top-4 right-4 rounded-full bg-ink/70 text-paper text-[11px] px-3 py-1 backdrop-blur">
                رسم توضيحي · وحدة تجريبية
              </span>
            </div>
            <div className="p-6">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-[900]">{listing.title}</h3>
                  <p className="text-sm text-muted mt-1">{formatEgp(listing.price_egp)}</p>
                </div>
                <AffordabilityBadge key={pid} status={aff.status} className="badge-pop text-sm px-3 py-1" />
              </div>
              <dl className="mt-5 grid grid-cols-3 gap-3 text-center">
                {[
                  ["المقدم المطلوب", plan.down_payment_egp],
                  ["القسط الشهري", plan.monthly_equivalent_egp],
                  ["دفعة الاستلام", plan.delivery_payment_egp],
                ].map(([k, v]) => (
                  <div key={k as string} className="rounded-2xl bg-sand/70 p-3">
                    <dt className="text-[11px] text-muted">{k}</dt>
                    <dd className="mt-1 text-sm font-[900]">{formatEgp(v as number | null)}</dd>
                  </div>
                ))}
              </dl>
              <p key={`r-${pid}`} className="msg-in mt-5 rounded-2xl border border-line/50 p-4 text-sm leading-relaxed">
                <span className="font-bold">ليه؟ </span>
                {aff.reason}
              </p>
              <p className="mt-3 text-[11px] text-muted">مثال توضيحي محسوب بالحاسبة التجريبية.</p>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
