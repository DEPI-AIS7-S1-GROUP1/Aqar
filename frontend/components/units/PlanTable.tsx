"use client";

import { useState } from "react";
import { FREQUENCY_LABEL, formatEgp, UNKNOWN } from "@/lib/format";
import type { Listing, PlanResult } from "@/lib/types";

const WARNING_TEXT: Record<string, string> = {
  delivery_payment_unknown: "دفعة الاستلام مش منشورة، فجدول الدفعات والقسط مش معروفين بالظبط.",
  delivery_month_unknown: "معاد الاستلام مش منشور، فمش عارفين نحط دفعة الاستلام في شهرها.",
  npv_unknown_payment_table: "جدول الدفعات مش كامل، فالقيمة الحالية مش محسوبة.",
  npv_unknown_delivery_payment: "القيمة الحالية مش محسوبة لأن دفعة الاستلام مش معروفة.",
  npv_unknown_delivery_month: "القيمة الحالية مش محسوبة لأن معاد الاستلام مش معروف.",
};

const TYPE_LABEL: Record<string, string> = {
  down_payment: "مقدم",
  installment: "قسط",
  delivery: "دفعة استلام",
  maintenance: "صيانة",
};

export default function PlanTable({ plan, listing }: { plan: PlanResult; listing: Listing }) {
  const [showAll, setShowAll] = useState(false);
  const rows = plan.payments ?? [];
  const visible = showAll ? rows : rows.slice(0, 6);

  const stats: [string, string][] = [
    ["المقدم", formatEgp(plan.down_payment_egp)],
    [
      `القسط (${listing.frequency ? FREQUENCY_LABEL[listing.frequency] : UNKNOWN})`,
      formatEgp(plan.installment_egp),
    ],
    ["ما يعادل شهريًا", formatEgp(plan.monthly_equivalent_egp)],
    ["دفعة الاستلام", formatEgp(plan.delivery_payment_egp)],
    ["عدد الأقساط", plan.installment_count === null ? UNKNOWN : plan.installment_count.toLocaleString("ar-EG")],
    ["الإجمالي (من غير صيانة)", formatEgp(plan.total_paid_egp)],
    [
      "القيمة الحالية (NPV)",
      plan.npv_egp === null
        ? UNKNOWN
        : `${formatEgp(plan.npv_egp)} بخصم ${plan.annual_discount_rate_pct?.toLocaleString("ar-EG")}٪ سنويًا`,
    ],
  ];

  return (
    <div>
      <dl className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {stats.map(([k, v]) => (
          <div key={k} className="rounded-2xl bg-sand/70 p-3">
            <dt className="text-[11px] text-muted">{k}</dt>
            <dd className={`mt-1 text-sm font-[900] ${v === UNKNOWN ? "text-muted" : "text-ink"}`}>{v}</dd>
          </div>
        ))}
      </dl>

      {plan.warnings.length > 0 && (
        <ul className="mt-4 flex flex-col gap-2">
          {plan.warnings.map((w) => (
            <li key={w} className="rounded-xl border border-warm/30 bg-[#FCEBC8]/60 text-[#7A4B00] px-3 py-2 text-xs leading-relaxed">
              {WARNING_TEXT[w] ?? w}
            </li>
          ))}
        </ul>
      )}

      {rows.length > 0 && (
        <div className="mt-5 rounded-2xl border border-line/50 overflow-hidden">
          <table className="w-full text-sm">
            <caption className="sr-only">جدول الدفعات</caption>
            <thead className="bg-sand text-muted text-xs">
              <tr>
                <th scope="col" className="text-right font-bold px-4 py-2">الشهر</th>
                <th scope="col" className="text-right font-bold px-4 py-2">النوع</th>
                <th scope="col" className="text-left font-bold px-4 py-2">المبلغ</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((p, k) => (
                <tr key={k} className="border-t border-line/40">
                  <td className="px-4 py-2">{p.month.toLocaleString("ar-EG")}</td>
                  <td className="px-4 py-2">{TYPE_LABEL[p.type]}</td>
                  <td className="px-4 py-2 text-left font-bold" dir="ltr">
                    {formatEgp(p.amount_egp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > 6 && (
            <button
              type="button"
              onClick={() => setShowAll((v) => !v)}
              className="w-full py-3 text-sm font-bold text-accent border-t border-line/40 hover:bg-sand/50"
            >
              {showAll ? "اعرض أقل" : `اعرض كل الدفعات (${rows.length.toLocaleString("ar-EG")})`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
