// Display helpers. Unknown (null/undefined/blank) shows "غير متوفر", never 0 and never blank.

export const UNKNOWN = "غير متوفر";

export function formatValue(val: unknown): string {
  if (val === null || val === undefined || val === "") return UNKNOWN;
  if (Array.isArray(val)) return val.length > 0 ? val.join("، ") : UNKNOWN;
  if (typeof val === "number") return val.toLocaleString("ar-EG");
  return String(val);
}

export function formatEgp(val: number | null | undefined): string {
  if (val === null || val === undefined) return UNKNOWN;
  return `${Math.round(val).toLocaleString("ar-EG")} ج.م`;
}

export function formatPct(val: number | null | undefined): string {
  if (val === null || val === undefined) return UNKNOWN;
  return `${val.toLocaleString("ar-EG")}٪`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return UNKNOWN;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return UNKNOWN;
  return d.toLocaleDateString("ar-EG", { year: "numeric", month: "long" });
}

export function formatTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleTimeString("ar-EG", { hour: "2-digit", minute: "2-digit" });
}

/** "منذ 5 دقائق" style. `now` is passed in so render stays pure. */
export function relativeTime(iso: string, now: number): string {
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return UNKNOWN;
  const mins = Math.max(0, Math.round((now - t) / 60000));
  if (mins < 1) return "دلوقتي";
  if (mins < 60) return `منذ ${mins.toLocaleString("ar-EG")} دقيقة`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `منذ ${hours.toLocaleString("ar-EG")} ساعة`;
  const days = Math.round(hours / 24);
  return `منذ ${days.toLocaleString("ar-EG")} يوم`;
}

export const AREAS: { key: string; label: string; short: string }[] = [
  { key: "new_cairo", label: "القاهرة الجديدة (التجمع)", short: "التجمع" },
  { key: "sheikh_zayed", label: "الشيخ زايد", short: "زايد" },
  { key: "october_6", label: "6 أكتوبر", short: "أكتوبر" },
  { key: "new_capital", label: "العاصمة الإدارية", short: "العاصمة" },
  { key: "mostakbal_city", label: "مستقبل سيتي", short: "مستقبل" },
  {
    key: "north_coast_ras_el_hekma",
    label: "الساحل الشمالي - رأس الحكمة",
    short: "الساحل",
  },
];

export function areaLabel(key: string | null | undefined): string {
  if (!key) return UNKNOWN;
  return AREAS.find((a) => a.key === key)?.label ?? key;
}

export const FREQUENCY_LABEL: Record<string, string> = {
  monthly: "شهري",
  quarterly: "ربع سنوي",
};

export const TIMELINE_LABEL: Record<string, string> = {
  "0-3m": "خلال 3 شهور",
  "3-12m": "من 3 لـ 12 شهر",
  "12m+": "أكتر من سنة",
  unknown: UNKNOWN,
};

export const PURPOSE_LABEL: Record<string, string> = {
  live: "سكن",
  invest: "استثمار",
};

export const TRIGGER_LABEL: Record<string, string> = {
  visit_or_reserve: "طلب معاينة أو حجز",
  human_request: "طلب يكلم حد من الفريق",
  sensitive_topic: "موضوع حساس (خصم / عقد)",
  ai_failure: "المساعد محتاج مساعدة",
  off_topic_limit: "رسائل كتير بره الموضوع",
};
