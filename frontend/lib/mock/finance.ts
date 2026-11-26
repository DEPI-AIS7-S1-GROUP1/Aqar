// DEMO-ONLY stand-in for backend/app/finance (Member 5). Used only when mocks are on.
// Same rules as the real calculator: unknown stays null, never 0; reasons contain no digits.
import type {
  AffordabilityResult,
  AffordabilityStatus,
  Listing,
  Payment,
  PlanResult,
} from "@/lib/types";

/** Payment schedules start here (deterministic for the demo). */
const PLAN_START = new Date("2026-12-01T00:00:00+02:00");
const TIGHT_LIMIT = 0.15;

function monthsUntil(iso: string | null): number | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  const m =
    (d.getFullYear() - PLAN_START.getFullYear()) * 12 +
    (d.getMonth() - PLAN_START.getMonth());
  return Math.max(1, m);
}

const round2 = (n: number) => Math.round(n * 100) / 100;

export function buildPlan(
  listing: Listing,
  annualDiscountRatePct: number | null = null
): PlanResult {
  const missing: string[] = [];
  const warnings: string[] = [];
  const price = listing.price_egp;

  const down =
    listing.down_payment_pct === null
      ? null
      : round2((price * listing.down_payment_pct) / 100);
  if (down === null) missing.push("down_payment_pct");

  const deliveryPct = listing.delivery_payment_pct;
  const delivery =
    deliveryPct === null ? null : round2((price * deliveryPct) / 100);
  if (delivery === null) {
    missing.push("delivery_payment_pct");
    warnings.push("delivery_payment_unknown");
  }

  const needsDeliveryMonth = (deliveryPct ?? 0) > 0;
  const deliveryMonth = monthsUntil(listing.delivery_date);
  if (needsDeliveryMonth && deliveryMonth === null) {
    missing.push("delivery_date");
    warnings.push("delivery_month_unknown");
  }

  const years = listing.years;
  const freq = listing.frequency;
  const count =
    years === null || freq === null ? null : years * (freq === "monthly" ? 12 : 4);
  if (count === null) missing.push("years_or_frequency");

  let installment: number | null = null;
  if (down !== null && delivery !== null && count !== null && count > 0) {
    installment = round2((price - down - delivery) / count);
  }

  let payments: Payment[] | null = null;
  const canBuildTable =
    installment !== null &&
    down !== null &&
    delivery !== null &&
    count !== null &&
    (!needsDeliveryMonth || deliveryMonth !== null);

  if (canBuildTable) {
    const step = freq === "monthly" ? 1 : 3;
    const rows: Payment[] = [{ month: 0, amount_egp: down!, type: "down_payment" }];
    let paid = down!;
    for (let i = 1; i <= count!; i++) {
      const isLast = i === count;
      const amount = isLast
        ? round2(price - delivery! - paid)
        : installment!;
      rows.push({ month: i * step, amount_egp: amount, type: "installment" });
      paid = round2(paid + amount);
    }
    if (delivery! > 0 && deliveryMonth !== null) {
      rows.push({ month: deliveryMonth, amount_egp: delivery!, type: "delivery" });
    }
    if (listing.maintenance_pct !== null && listing.maintenance_pct > 0) {
      rows.push({
        month: deliveryMonth ?? (count! * step),
        amount_egp: round2((price * listing.maintenance_pct) / 100),
        type: "maintenance",
      });
    }
    rows.sort((a, b) => a.month - b.month);
    payments = rows;
  } else if (!warnings.includes("delivery_payment_unknown")) {
    warnings.push("npv_unknown_payment_table");
  }

  let npv: number | null = null;
  if (payments && annualDiscountRatePct !== null) {
    const m = Math.pow(1 + annualDiscountRatePct / 100, 1 / 12) - 1;
    npv = round2(
      payments
        .filter((p) => p.type !== "maintenance")
        .reduce((s, p) => s + p.amount_egp / Math.pow(1 + m, p.month), 0)
    );
  }

  return {
    listing_id: listing.listing_id,
    plan_id: `P-${listing.listing_id}`,
    plan_type: "developer",
    price_egp: price,
    down_payment_egp: down,
    down_payment_pct: listing.down_payment_pct,
    delivery_payment_egp: delivery,
    delivery_month: needsDeliveryMonth ? deliveryMonth : null,
    installment_count: count,
    installment_egp: installment,
    monthly_equivalent_egp:
      installment === null ? null : round2(installment / (freq === "quarterly" ? 3 : 1)),
    total_paid_egp: payments ? price : null,
    npv_egp: npv,
    annual_discount_rate_pct: npv === null ? null : annualDiscountRatePct,
    payments,
    missing_fields: missing,
    warnings,
  };
}

export function checkAffordability(
  plan: PlanResult,
  downAvailable: number | null,
  monthlyCapacity: number | null
): AffordabilityResult {
  const missing: string[] = [];
  if (downAvailable === null) missing.push("down_payment_available_egp");
  if (monthlyCapacity === null) missing.push("monthly_capacity_egp");
  if (plan.down_payment_egp === null) missing.push("down_payment_egp");
  if (plan.monthly_equivalent_egp === null) missing.push("monthly_equivalent_egp");

  const base = {
    listing_id: plan.listing_id,
    plan_id: plan.plan_id,
    down_payment_required_egp: plan.down_payment_egp,
    down_payment_available_egp: downAvailable,
    monthly_required_egp: plan.monthly_equivalent_egp,
    monthly_capacity_egp: monthlyCapacity,
  };

  if (missing.length > 0) {
    return {
      ...base,
      status: "unknown",
      reason: "ناقص بيانات عشان نحكم على القدرة على الدفع.",
      down_payment_gap_egp: null,
      monthly_gap_egp: null,
      flags: [],
      missing_fields: missing,
    };
  }

  const downReq = plan.down_payment_egp!;
  const monReq = plan.monthly_equivalent_egp!;
  const downGap = round2(downReq - downAvailable!);
  const monGap = round2(monReq - monthlyCapacity!);
  const over = Math.max(
    downAvailable! > 0 ? downReq / downAvailable! - 1 : downReq > 0 ? 1 : 0,
    monthlyCapacity! > 0 ? monReq / monthlyCapacity! - 1 : monReq > 0 ? 1 : 0
  );
  const deliveryUncovered =
    (plan.delivery_payment_egp ?? 0) > 0 &&
    downAvailable! - downReq < (plan.delivery_payment_egp ?? 0);

  let status: AffordabilityStatus;
  let reason: string;
  const flags: string[] = deliveryUncovered ? ["delivery_payment"] : [];
  if (over > TIGHT_LIMIT) {
    status = "not_fit";
    reason = deliveryUncovered
      ? "المقدم أو القسط أعلى بكتير من حدودك، وكمان دفعة الاستلام مش متغطية."
      : "المقدم أو القسط أعلى بكتير من الحدود اللي حضرتك قلتها.";
  } else if (over > 0) {
    status = "tight";
    reason = "قريبة من حدودك، بس القسط أو المقدم أعلى شوية من اللي قلته.";
  } else if (deliveryUncovered) {
    status = "tight";
    reason = "المقدم والقسط مناسبين، بس دفعة الاستلام مش متغطية من المقدم المتاح.";
  } else {
    status = "fit";
    reason = "المقدم والقسط في حدود اللي حضرتك قلته.";
  }

  return {
    ...base,
    status,
    reason,
    down_payment_gap_egp: downGap,
    monthly_gap_egp: monGap,
    flags,
    missing_fields: [],
  };
}
