"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import CustomerHeader from "@/components/ui/CustomerHeader";
import Reveal from "@/components/motion/Reveal";
import PhotoGallery from "@/components/units/PhotoGallery";
import PlanTable from "@/components/units/PlanTable";
import { api, ApiError } from "@/lib/api";
import { areaLabel, formatDate, formatEgp, formatPct, formatValue, FREQUENCY_LABEL, UNKNOWN } from "@/lib/format";
import type { Listing, PlanResult } from "@/lib/types";

export default function UnitDetailClient() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [listing, setListing] = useState<Listing | null>(null);
  const [others, setOthers] = useState<Listing[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [rate, setRate] = useState(20);
  const [plans, setPlans] = useState<{ rate: number; items: PlanResult[] } | null>(null);
  const [compareWith, setCompareWith] = useState("");

  useEffect(() => {
    let alive = true;
    api
      .listing(id)
      .then((l) => {
        if (!alive) return;
        setListing(l);
        api.viewListing(l.listing_id);
        api.listings({ area: l.area, limit: 20 }).then((p) => alive && setOthers(p.items.filter((x) => x.listing_id !== l.listing_id)));
      })
      .catch((e) => alive && setError(e instanceof ApiError ? e.message : "حصلت مشكلة."));
    return () => {
      alive = false;
    };
  }, [id]);

  useEffect(() => {
    let alive = true;
    const t = setTimeout(() => {
      api
        .plans(id, rate)
        .then((items) => alive && setPlans({ rate, items }))
        .catch(() => alive && setPlans({ rate, items: [] }));
    }, 250);
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, [id, rate]);

  if (error) {
    return (
      <div className="min-h-[100svh] bg-paper">
        <CustomerHeader />
        <main className="max-w-md mx-auto px-4 py-24 text-center">
          <h1 className="text-2xl font-[900] text-ink">{error}</h1>
          <Link href="/listings" className="mt-6 inline-block bg-ink text-paper px-6 py-3 rounded-full font-bold">ارجع للوحدات</Link>
        </main>
      </div>
    );
  }

  const plan = plans?.items[0] ?? null;

  return (
    <div className="min-h-[100svh] bg-paper">
      <CustomerHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <Link href="/listings" className="text-sm font-bold text-muted hover:text-ink">← كل الوحدات</Link>

        {!listing ? (
          <div className="mt-6 grid lg:grid-cols-2 gap-8">
            <div className="skeleton aspect-[16/10] rounded-[28px]" />
            <div className="flex flex-col gap-4">
              <div className="skeleton h-10 w-2/3 rounded-xl" />
              <div className="skeleton h-6 w-1/3 rounded-xl" />
              <div className="skeleton h-40 rounded-2xl" />
            </div>
          </div>
        ) : (
          <>
            <div className="mt-6 grid lg:grid-cols-[1.15fr_1fr] gap-8 items-start">
              <Reveal variant="scale">
                <PhotoGallery listing={listing} />
              </Reveal>
              <Reveal delay={120}>
                <p className="text-accent font-bold text-sm">{areaLabel(listing.area)}</p>
                <h1 className="mt-2 text-3xl sm:text-4xl font-[900] tracking-tight text-ink leading-tight">
                  {listing.title ?? `وحدة ${listing.listing_id}`}
                </h1>
                <p className="mt-3 text-3xl font-[900] text-ink">{formatEgp(listing.price_egp)}</p>
                <dl className="mt-6 grid grid-cols-2 gap-3 text-sm">
                  {(
                    [
                      ["النوع", formatValue(listing.unit_type)],
                      ["المساحة", listing.area_sqm ? `${listing.area_sqm.toLocaleString("ar-EG")} م²` : UNKNOWN],
                      ["الغرف", formatValue(listing.bedrooms)],
                      ["المطور", listing.developer],
                      ["الاستلام", formatDate(listing.delivery_date)],
                      ["المقدم", formatPct(listing.down_payment_pct)],
                      ["السنين", formatValue(listing.years)],
                      ["الدفع", listing.frequency ? FREQUENCY_LABEL[listing.frequency] : UNKNOWN],
                      ["دفعة الاستلام", formatPct(listing.delivery_payment_pct)],
                      ["الصيانة", formatPct(listing.maintenance_pct)],
                    ] as [string, string][]
                  ).map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between gap-3 border-b border-line/50 pb-2">
                      <dt className="text-muted">{k}</dt>
                      <dd className={`font-bold ${v === UNKNOWN ? "text-muted font-normal" : "text-ink"}`}>{v}</dd>
                    </div>
                  ))}
                </dl>
                <div className="mt-7 flex flex-wrap gap-3">
                  <Link
                    href={`/chat?ask=${encodeURIComponent(listing.listing_id)}`}
                    className="bg-accent text-paper px-6 py-3.5 rounded-full font-bold shadow-lg shadow-accent/25 hover:-translate-y-[2px] transition-transform"
                  >
                    اسأل المساعد عن الوحدة دي
                  </Link>
                  <form
                    className="flex items-center gap-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (compareWith) router.push(`/compare?ids=${listing.listing_id},${compareWith}`);
                    }}
                  >
                    <label htmlFor="cmp" className="sr-only">قارن مع</label>
                    <select
                      id="cmp"
                      value={compareWith}
                      onChange={(e) => setCompareWith(e.target.value)}
                      className="min-h-[48px] rounded-full border border-line bg-white px-4 text-sm"
                    >
                      <option value="">قارن مع وحدة تانية…</option>
                      {others.map((o) => (
                        <option key={o.listing_id} value={o.listing_id}>
                          {o.title ?? o.listing_id}
                        </option>
                      ))}
                    </select>
                    <button type="submit" disabled={!compareWith} className="min-h-[48px] px-5 rounded-full bg-ink text-paper text-sm font-bold disabled:opacity-40">
                      قارن
                    </button>
                  </form>
                </div>
                {listing.notes && <p className="mt-5 text-xs text-muted">{listing.notes}</p>}
              </Reveal>
            </div>

            <Reveal className="mt-12">
              <div className="bg-white rounded-[28px] border border-line/50 p-5 sm:p-8">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-[900] text-ink">خطة السداد</h2>
                    <p className="mt-1 text-sm text-muted">كل الأرقام من الحاسبة. اللي مش منشور بيظهر «{UNKNOWN}».</p>
                  </div>
                  <label className="flex flex-col gap-1 text-xs font-bold text-muted min-w-[220px]">
                    نسبة الخصم السنوية للقيمة الحالية: {rate.toLocaleString("ar-EG")}٪
                    <input type="range" min={0} max={40} step={1} value={rate} onChange={(e) => setRate(Number(e.target.value))} className="accent-[#C8372F]" />
                  </label>
                </div>
                <div className="mt-6">
                  {plan ? (
                    <PlanTable plan={plan} listing={listing} />
                  ) : plans ? (
                    <p className="text-sm text-muted">مفيش خطة سداد منشورة للوحدة دي.</p>
                  ) : (
                    <div className="skeleton h-40 rounded-2xl" />
                  )}
                </div>
              </div>
            </Reveal>
          </>
        )}
      </main>
    </div>
  );
}
