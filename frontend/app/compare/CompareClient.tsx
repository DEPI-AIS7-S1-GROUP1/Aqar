"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import CustomerHeader from "@/components/ui/CustomerHeader";
import Reveal from "@/components/motion/Reveal";
import CompareCard from "@/components/units/CompareCard";
import { api, ApiError } from "@/lib/api";
import type { CompareResult } from "@/lib/types";

export default function CompareClient() {
  const sp = useSearchParams();
  const idsKey = sp.get("ids") ?? "";
  const [rate, setRate] = useState(20);
  const [res, setRes] = useState<{ k: string; data: CompareResult | null; error: string | null } | null>(null);
  const k = `${idsKey}|${rate}`;

  useEffect(() => {
    let alive = true;
    const ids = idsKey.split(",").filter(Boolean);
    const t = setTimeout(() => {
      api
        .compare(ids, rate)
        .then((data) => alive && setRes({ k: `${idsKey}|${rate}`, data, error: null }))
        .catch((e) => alive && setRes({ k: `${idsKey}|${rate}`, data: null, error: e instanceof ApiError ? e.message : "حصلت مشكلة." }));
    }, 200);
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, [idsKey, rate]);

  return (
    <div className="min-h-[100svh] bg-paper">
      <CustomerHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <Reveal className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <p className="text-accent font-bold text-sm">مقارنة</p>
            <h1 className="mt-2 text-4xl font-[900] tracking-tight text-ink">الخطط جنب بعض.</h1>
            <p className="mt-2 text-sm text-muted">اللي عليه «الأقل» هو الأوفر في الصف ده. لو سجلت دخول ومعاك بحث، هتشوف كمان شارة القدرة على الدفع.</p>
          </div>
          <label className="flex flex-col gap-1 text-xs font-bold text-muted min-w-[220px]">
            نسبة الخصم السنوية: {rate.toLocaleString("ar-EG")}٪
            <input type="range" min={0} max={40} step={1} value={rate} onChange={(e) => setRate(Number(e.target.value))} className="accent-[#C8372F]" />
          </label>
        </Reveal>

        <div className="mt-8">
          {res?.error ? (
            <div className="rounded-[24px] bg-white border border-line/50 p-10 text-center">
              <p className="font-bold text-ink">{res.error}</p>
              <Link href="/listings" className="mt-5 inline-block bg-ink text-paper px-6 py-3 rounded-full font-bold">اختار وحدات من الصفحة</Link>
            </div>
          ) : res?.data ? (
            <div className={`transition-opacity ${res.k === k ? "opacity-100" : "opacity-60"}`}>
              <CompareCard items={res.data.items} />
            </div>
          ) : (
            <div className="skeleton h-[480px] rounded-[24px]" />
          )}
        </div>
      </main>
    </div>
  );
}
