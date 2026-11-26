"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import RequireRole from "@/components/auth/RequireRole";
import BrokerHeader from "@/components/broker/BrokerHeader";
import Reveal from "@/components/motion/Reveal";
import { api, ApiError } from "@/lib/api";
import { areaLabel, UNKNOWN } from "@/lib/format";
import type { AnalyticsResult, CountItem } from "@/lib/types";

const BAND_META = [
  { key: "hot", label: "Hot", color: "bg-hot" },
  { key: "warm", label: "Warm", color: "bg-warm" },
  { key: "cold", label: "Cold", color: "bg-cold" },
];

function Bars({ items, label, color = "bg-ink", href }: { items: CountItem[]; label: (k: string) => string; color?: string; href?: (k: string) => string }) {
  const max = Math.max(1, ...items.map((i) => i.count));
  if (!items.length) return <p className="text-sm text-muted">لسه مفيش بيانات.</p>;
  return (
    <ul className="flex flex-col gap-3">
      {items.map((it, i) => {
        const name = label(it.key);
        return (
          <li key={it.key}>
            <div className="flex items-center justify-between text-sm mb-1">
              {href ? (
                <Link href={href(it.key)} className="font-bold hover:text-accent">{name}</Link>
              ) : (
                <span className="font-bold">{name}</span>
              )}
              <span className="text-muted">{it.count.toLocaleString("ar-EG")}</span>
            </div>
            <div className="h-3 rounded-full bg-sand overflow-hidden">
              <div className={`bar-grow h-full rounded-full ${color}`} style={{ width: `${(it.count / max) * 100}%`, animationDelay: `${i * 90}ms` }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

function AnalyticsInner() {
  const [data, setData] = useState<AnalyticsResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const load = () =>
      api
        .analytics()
        .then((d) => alive && setData(d))
        .catch((e) => alive && setError(e instanceof ApiError ? e.message : "مش قادرين نجيب التحليلات."));
    load();
    const t = setInterval(() => !document.hidden && load(), 10000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const total = data ? Object.values(data.leads_by_band).reduce((a, b) => a + b, 0) : 0;

  return (
    <div className="min-h-[100svh] bg-sand">
      <BrokerHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-8">
        <h1 className="text-2xl sm:text-3xl font-[900] text-ink tracking-tight">التحليلات</h1>
        <p className="text-sm text-muted mt-1">بتتحدث كل 10 ثواني.</p>
        {error && <p role="alert" className="mt-4 rounded-2xl bg-[#FBDADA] text-[#7F1D1D] px-4 py-3 text-sm">{error}</p>}

        {!data ? (
          <div className="mt-6 grid md:grid-cols-2 gap-5">
            {Array.from({ length: 4 }, (_, i) => <div key={i} className="skeleton h-56 rounded-2xl" />)}
          </div>
        ) : (
          <div className="mt-6 grid md:grid-cols-2 gap-5">
            <Reveal className="bg-white rounded-2xl border border-line/40 p-6">
              <h2 className="font-[900] text-ink">العملاء حسب التقييم</h2>
              <div className="mt-5 flex h-4 rounded-full overflow-hidden bg-sand" aria-hidden>
                {BAND_META.map((b) => (
                  <div key={b.key} className={`bar-grow ${b.color}`} style={{ width: total ? `${((data.leads_by_band[b.key] ?? 0) / total) * 100}%` : 0 }} />
                ))}
              </div>
              <dl className="mt-5 grid grid-cols-3 gap-3 text-center">
                {BAND_META.map((b) => (
                  <div key={b.key} className="rounded-xl bg-sand/60 p-3">
                    <dt className="text-xs text-muted flex items-center justify-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${b.color}`} />
                      {b.label}
                    </dt>
                    <dd className="mt-1 text-2xl font-[900]">{(data.leads_by_band[b.key] ?? 0).toLocaleString("ar-EG")}</dd>
                  </div>
                ))}
              </dl>
            </Reveal>

            <Reveal delay={100} className="bg-white rounded-2xl border border-line/40 p-6">
              <h2 className="font-[900] text-ink">أداء النظام</h2>
              <dl className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-sand/60 p-4">
                  <dt className="text-xs text-muted">زمن الرد (p95)</dt>
                  <dd className="mt-1 text-2xl font-[900]">
                    {data.p95_latency_ms === null ? <span className="text-base text-muted font-normal">{UNKNOWN}</span> : `${data.p95_latency_ms.toLocaleString("ar-EG")} ms`}
                  </dd>
                </div>
                <div className="rounded-xl bg-sand/60 p-4">
                  <dt className="text-xs text-muted">نسبة الـ cache hit</dt>
                  <dd className="mt-1 text-2xl font-[900]">
                    {data.cache_hit_rate === null ? <span className="text-base text-muted font-normal">{UNKNOWN}</span> : `${Math.round(data.cache_hit_rate * 100).toLocaleString("ar-EG")}٪`}
                  </dd>
                </div>
              </dl>
            </Reveal>

            <Reveal delay={150} className="bg-white rounded-2xl border border-line/40 p-6">
              <h2 className="font-[900] text-ink">أكتر المناطق طلبًا</h2>
              <div className="mt-5">
                <Bars items={data.top_areas} label={areaLabel} color="bg-accent" />
              </div>
            </Reveal>

            <Reveal delay={200} className="bg-white rounded-2xl border border-line/40 p-6">
              <h2 className="font-[900] text-ink">أكتر الوحدات مشاهدة</h2>
              <div className="mt-5">
                <Bars items={data.top_listings} label={(k) => `وحدة ${k}`} color="bg-cold" href={(k) => `/listings/${k}`} />
              </div>
            </Reveal>
          </div>
        )}
      </main>
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <RequireRole role="broker">
      <AnalyticsInner />
    </RequireRole>
  );
}
