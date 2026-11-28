import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import { UnitPhoto } from "./UnitCard";
import { areaLabel, formatDate, formatEgp, UNKNOWN } from "@/lib/format";
import type { UnitCard } from "@/lib/types";

type Row = { label: string; get: (c: UnitCard) => string; best?: (cards: UnitCard[]) => number | null };

function minIndex(vals: (number | null)[]): number | null {
  let best: number | null = null;
  vals.forEach((v, i) => {
    if (v === null) return;
    if (best === null || v < (vals[best] as number)) best = i;
  });
  return vals.filter((v) => v !== null).length >= 2 ? best : null;
}

const ROWS: Row[] = [
  { label: "المنطقة", get: (c) => areaLabel(c.listing.area) },
  { label: "السعر", get: (c) => formatEgp(c.listing.price_egp), best: (cs) => minIndex(cs.map((c) => c.listing.price_egp)) },
  { label: "المقدم", get: (c) => formatEgp(c.plan?.down_payment_egp), best: (cs) => minIndex(cs.map((c) => c.plan?.down_payment_egp ?? null)) },
  { label: "ما يعادل شهريًا", get: (c) => formatEgp(c.plan?.monthly_equivalent_egp), best: (cs) => minIndex(cs.map((c) => c.plan?.monthly_equivalent_egp ?? null)) },
  { label: "دفعة الاستلام", get: (c) => formatEgp(c.plan?.delivery_payment_egp) },
  { label: "عدد السنين", get: (c) => (c.listing.years === null ? UNKNOWN : `${c.listing.years.toLocaleString("ar-EG")} سنين`) },
  { label: "الاستلام", get: (c) => formatDate(c.listing.delivery_date) },
  { label: "الإجمالي", get: (c) => formatEgp(c.plan?.total_paid_egp) },
  { label: "القيمة الحالية", get: (c) => formatEgp(c.plan?.npv_egp), best: (cs) => minIndex(cs.map((c) => c.plan?.npv_egp ?? null)) },
];

export default function CompareCard({ items, compact = false }: { items: UnitCard[]; compact?: boolean }) {
  const rate = items.find((c) => c.plan?.annual_discount_rate_pct !== null)?.plan?.annual_discount_rate_pct ?? null;
  return (
    <div className="bg-white text-ink rounded-[24px] border border-line/50 overflow-x-auto">
      <table className="w-full text-sm min-w-[480px]">
        <caption className="sr-only">مقارنة خطط السداد</caption>
        <thead>
          <tr>
            <th scope="col" className="w-32" />
            {items.map((c) => (
              <th key={c.listing.listing_id} scope="col" className="p-3 align-top text-right">
                {!compact && <UnitPhoto listing={c.listing} className="h-28 rounded-2xl mb-3" variant="dusk" />}
                <div className="font-bold leading-snug">{c.listing.title ?? c.listing.listing_id}</div>
                <div className="mt-2">
                  {c.affordability ? <AffordabilityBadge status={c.affordability.status} /> : <span className="text-xs text-muted">القدرة: {UNKNOWN}</span>}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map((r) => {
            const best = r.best?.(items) ?? null;
            return (
              <tr key={r.label} className="border-t border-line/40">
                <th scope="row" className="p-3 text-right text-xs text-muted font-bold">{r.label}</th>
                {items.map((c, i) => {
                  const v = r.get(c);
                  return (
                    <td key={c.listing.listing_id} className={`p-3 font-bold ${v === UNKNOWN ? "text-muted font-normal" : ""}`}>
                      {v}
                      {best === i && <span className="mr-2 inline-block rounded-full bg-[#DDF1E4] text-[#14532D] text-[10px] px-2 py-0.5">الأقل</span>}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="px-4 py-3 text-[11px] text-muted border-t border-line/40">
        {rate === null ? "القيمة الحالية بتتحسب لما تختار نسبة خصم." : `القيمة الحالية محسوبة بخصم ${rate.toLocaleString("ar-EG")}٪ سنويًا.`} كل الأرقام من الحاسبة.
      </p>
    </div>
  );
}
