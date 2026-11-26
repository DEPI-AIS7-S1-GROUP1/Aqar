"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import CustomerHeader from "@/components/ui/CustomerHeader";
import Reveal from "@/components/motion/Reveal";
import UnitCard from "@/components/units/UnitCard";
import { api, ApiError } from "@/lib/api";
import { AREAS } from "@/lib/format";
import type { ListingPage } from "@/lib/types";

const PAGE = 9;

export default function ListingsClient() {
  const router = useRouter();
  const sp = useSearchParams();
  const key = sp.toString();
  const area = sp.get("area") ?? "";
  const minPrice = sp.get("min_price") ?? "";
  const maxPrice = sp.get("max_price") ?? "";
  const before = sp.get("delivery_before") ?? "";
  const beds = sp.get("bedrooms_min") ?? "";
  const offset = Number(sp.get("offset") ?? 0);

  const [data, setData] = useState<{ key: string; page: ListingPage | null; error: string | null } | null>(null);
  const [picked, setPicked] = useState<string[]>([]);
  const loading = data?.key !== key;

  useEffect(() => {
    let alive = true;
    const p = new URLSearchParams(key);
    api
      .listings({
        area: p.get("area") || undefined,
        min_price: p.get("min_price") ? Number(p.get("min_price")) : undefined,
        max_price: p.get("max_price") ? Number(p.get("max_price")) : undefined,
        delivery_before: p.get("delivery_before") || undefined,
        bedrooms_min: p.get("bedrooms_min") ? Number(p.get("bedrooms_min")) : undefined,
        limit: PAGE,
        offset: Number(p.get("offset") ?? 0),
      })
      .then((page) => alive && setData({ key, page, error: null }))
      .catch((e) => alive && setData({ key, page: null, error: e instanceof ApiError ? e.message : "حصلت مشكلة." }));
    return () => {
      alive = false;
    };
  }, [key]);

  function apply(next: Record<string, string>) {
    const p = new URLSearchParams(key);
    Object.entries(next).forEach(([k, v]) => (v ? p.set(k, v) : p.delete(k)));
    if (!("offset" in next)) p.delete("offset");
    router.replace(`/listings${p.toString() ? `?${p}` : ""}`, { scroll: false });
  }

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    apply({
      area: String(f.get("area") ?? ""),
      min_price: String(f.get("min_price") ?? ""),
      max_price: String(f.get("max_price") ?? ""),
      delivery_before: String(f.get("delivery_before") ?? ""),
      bedrooms_min: String(f.get("bedrooms_min") ?? ""),
    });
  }

  const toggle = (id: string) =>
    setPicked((v) => (v.includes(id) ? v.filter((x) => x !== id) : v.length >= 3 ? v : [...v, id]));

  const page = data?.page;
  const total = page?.total ?? 0;

  return (
    <div className="min-h-[100svh] bg-paper">
      <CustomerHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
        <Reveal>
          <p className="text-accent font-bold text-sm">الوحدات</p>
          <h1 className="mt-2 text-4xl sm:text-5xl font-[900] tracking-tight text-ink">استكشف براحتك.</h1>
          <p className="mt-3 text-muted max-w-xl">فلتر بالمنطقة والسعر والاستلام. عايز ترشيحات على قد مقدمك وقسطك؟ <Link href="/chat" className="text-accent font-bold hover:underline">اسأل المساعد</Link>.</p>
        </Reveal>

        <form key={key} onSubmit={onSubmit} className="mt-8 grid grid-cols-2 md:grid-cols-6 gap-3 bg-white border border-line/50 rounded-[24px] p-4 shadow-sm" aria-label="فلاتر البحث">
          <label className="col-span-2 flex flex-col gap-1 text-xs font-bold text-muted">
            المنطقة
            <select name="area" defaultValue={area} className="min-h-[44px] rounded-xl border border-line px-3 text-sm text-ink bg-paper/50">
              <option value="">كل المناطق</option>
              {AREAS.map((a) => (
                <option key={a.key} value={a.key}>{a.label}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-xs font-bold text-muted">
            أقل سعر
            <input name="min_price" type="number" inputMode="numeric" min={0} step={100000} defaultValue={minPrice} placeholder="مثلاً 2000000" className="min-h-[44px] rounded-xl border border-line px-3 text-sm text-ink bg-paper/50" />
          </label>
          <label className="flex flex-col gap-1 text-xs font-bold text-muted">
            أعلى سعر
            <input name="max_price" type="number" inputMode="numeric" min={0} step={100000} defaultValue={maxPrice} placeholder="مثلاً 6000000" className="min-h-[44px] rounded-xl border border-line px-3 text-sm text-ink bg-paper/50" />
          </label>
          <label className="flex flex-col gap-1 text-xs font-bold text-muted">
            استلام قبل
            <input name="delivery_before" type="date" defaultValue={before} className="min-h-[44px] rounded-xl border border-line px-3 text-sm text-ink bg-paper/50" />
          </label>
          <label className="flex flex-col gap-1 text-xs font-bold text-muted">
            غرف على الأقل
            <select name="bedrooms_min" defaultValue={beds} className="min-h-[44px] rounded-xl border border-line px-3 text-sm text-ink bg-paper/50">
              <option value="">أي عدد</option>
              {[1, 2, 3, 4].map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </label>
          <div className="col-span-2 md:col-span-6 flex flex-wrap items-center gap-3">
            <button type="submit" className="min-h-[44px] px-6 rounded-full bg-ink text-paper text-sm font-bold hover:bg-accent transition-colors">
              ابحث
            </button>
            {(area || minPrice || maxPrice || before || beds) && (
              <button type="button" onClick={() => router.replace("/listings", { scroll: false })} className="min-h-[44px] px-4 rounded-full text-sm font-bold text-muted hover:text-ink">
                امسح الفلاتر
              </button>
            )}
            <span className="text-sm text-muted mr-auto" aria-live="polite">
              {loading ? "بندوّر..." : data?.error ? "" : `${total.toLocaleString("ar-EG")} وحدة`}
            </span>
          </div>
        </form>

        {/* quick area chips */}
        <div className="mt-5 flex flex-wrap gap-2">
          {AREAS.map((a) => (
            <button
              key={a.key}
              type="button"
              onClick={() => apply({ area: area === a.key ? "" : a.key })}
              className={`rounded-full px-4 py-2 text-xs font-bold border transition-all ${
                area === a.key ? "bg-accent text-paper border-accent" : "bg-white border-line/60 text-muted hover:text-ink hover:border-ink/40"
              }`}
            >
              {a.short}
            </button>
          ))}
        </div>

        {data?.error && (
          <p role="alert" className="mt-8 rounded-2xl bg-[#FBDADA] text-[#7F1D1D] px-4 py-3 text-sm">{data.error}</p>
        )}

        <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading
            ? Array.from({ length: 6 }, (_, i) => <div key={i} className="skeleton h-80 rounded-[20px]" />)
            : page?.items.map((l, i) => (
                <Reveal key={l.listing_id} delay={(i % 3) * 90} className="h-full">
                  <UnitCard listing={l} selected={picked.includes(l.listing_id)} onToggleSelect={() => toggle(l.listing_id)} />
                </Reveal>
              ))}
        </div>

        {!loading && page && page.items.length === 0 && (
          <div className="mt-6 rounded-[24px] bg-white border border-line/50 p-10 text-center">
            <p className="font-bold text-ink">مفيش وحدات بالفلاتر دي.</p>
            <p className="mt-1 text-sm text-muted">جرّب توسّع نطاق السعر أو تشيل فلتر الاستلام.</p>
          </div>
        )}

        {page && total > PAGE && (
          <nav className="mt-10 flex items-center justify-center gap-3" aria-label="الصفحات">
            <button type="button" disabled={offset === 0} onClick={() => apply({ offset: String(Math.max(0, offset - PAGE)) })} className="px-5 py-2.5 rounded-full border border-line text-sm font-bold disabled:opacity-40">
              السابق
            </button>
            <span className="text-sm text-muted">
              {(Math.floor(offset / PAGE) + 1).toLocaleString("ar-EG")} من {Math.ceil(total / PAGE).toLocaleString("ar-EG")}
            </span>
            <button type="button" disabled={offset + PAGE >= total} onClick={() => apply({ offset: String(offset + PAGE) })} className="px-5 py-2.5 rounded-full border border-line text-sm font-bold disabled:opacity-40">
              التالي
            </button>
          </nav>
        )}
      </main>

      {/* compare tray */}
      <div
        className={`fixed bottom-5 inset-x-4 sm:inset-x-auto sm:left-1/2 sm:-translate-x-1/2 z-30 transition-all duration-500 ${
          picked.length ? "translate-y-0 opacity-100" : "translate-y-24 opacity-0 pointer-events-none"
        }`}
      >
        <div className="bg-ink text-paper rounded-full shadow-2xl pl-2 pr-5 py-2 flex items-center gap-4">
          <span className="text-sm">
            {picked.length.toLocaleString("ar-EG")} مختارة {picked.length < 2 && "· اختار كمان واحدة"}
          </span>
          <button type="button" onClick={() => setPicked([])} className="text-xs text-muted-dark hover:text-paper">مسح</button>
          <Link
            href={picked.length >= 2 ? `/compare?ids=${picked.join(",")}` : "#"}
            aria-disabled={picked.length < 2}
            className={`rounded-full px-5 py-2.5 text-sm font-bold ${picked.length >= 2 ? "bg-accent" : "bg-paper/10 pointer-events-none text-muted-dark"}`}
          >
            قارن الخطط
          </Link>
        </div>
      </div>
    </div>
  );
}
