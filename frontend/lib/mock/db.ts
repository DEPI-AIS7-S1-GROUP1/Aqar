// DEMO-ONLY in-browser backend state, used when mocks are on.
// Stored in localStorage so a customer tab and a broker tab see the same demo (split-screen demo).
// Real mode never touches this file.
import type {
  AffordabilityStatus,
  Band,
  Listing,
  MessageRole,
  Mode,
  Purpose,
  Role,
  Timeline,
} from "@/lib/types";

export interface MockUser {
  user_id: string;
  email: string;
  name: string;
  role: Role;
  password: string;
  created_at: string;
}

export interface StoredMessage {
  message_id: string;
  role: MessageRole;
  text: string;
  created_at: string;
  card_listing_ids: string[];
}

export interface MockSlots {
  areas: string[] | null;
  down_payment_available_egp: number | null;
  monthly_capacity_egp: number | null;
  timeline: Timeline | null;
  purpose: Purpose | null;
}

export interface MockConversation {
  conversation_id: string;
  lead_id: string;
  user_id: string;
  mode: Mode;
  messages: StoredMessage[];
  slots: MockSlots;
  score: number;
  band: Band;
  reasons: string[];
  shown: string[];
  statuses: Record<string, AffordabilityStatus>;
  liked: Record<string, boolean>;
  visit_requested: boolean;
  trigger: string | null;
  taken_by: string | null;
  updated_at: string;
}

export interface MockState {
  version: 3;
  seq: number;
  users: MockUser[];
  conversations: MockConversation[];
  views: Record<string, number>;
  latencies: number[];
}

const KEY = "aqarai-demo-db-v3";

export const LISTINGS: Listing[] = [
  L("NC-101", "new_cairo", "شركة النيل للتطوير (تجريبي)", 4800000, 145, "2028-06-30", 10, 8, "quarterly", 10, 8, "شقة 3 غرف في كمبوند بالتجمع", "شقة", 3),
  L("NC-102", "new_cairo", "دلتا للتعمير (تجريبي)", 3600000, 120, null, 0, 10, "monthly", null, null, "شقة غرفتين بمقدم صفر", "شقة", 2),
  L("NC-103", "new_cairo", "حورس العقارية (تجريبي)", 6200000, 165, "2029-03-31", 5, 8, "monthly", 0, 8, "شقة 3 غرف بحديقة خاصة", "شقة بحديقة", 3),
  L("SZ-201", "sheikh_zayed", "شركة النيل للتطوير (تجريبي)", 9250000, 210, "2027-12-31", 15, 6, "quarterly", 0, 10, "دوبلكس 4 غرف في زايد", "دوبلكس", 4),
  L("SZ-202", "sheikh_zayed", "لوتس للتطوير (تجريبي)", 7400000, 190, "2028-09-30", 10, 7, "monthly", 5, 7, "تاون هاوس 3 غرف", "تاون هاوس", 3),
  L("OC-301", "october_6", "الأهرام للتعمير (تجريبي)", 2900000, 110, "2027-06-30", 10, 6, "monthly", 10, 5, "شقة غرفتين قريبة من المحور", "شقة", 2),
  L("NA-401", "new_capital", "المسلة للتطوير (تجريبي)", 5100000, 150, "2028-12-31", 10, 8, "monthly", 10, 8, "شقة 3 غرف في الحي السكني", "شقة", 3),
  L("MC-501", "mostakbal_city", "دلتا للتعمير (تجريبي)", 3900000, 125, "2029-06-30", 5, 9, "monthly", 5, 6, "شقة غرفتين في مستقبل سيتي", "شقة", 2),
  L("NCO-601", "north_coast_ras_el_hekma", "المتوسط للمنتجعات (تجريبي)", 8600000, 105, "2028-06-30", 10, 8, "quarterly", 15, 10, "شاليه غرفتين على البحر", "شاليه", 2),
];

function L(
  id: string,
  area: string,
  developer: string,
  price: number,
  sqm: number,
  delivery: string | null,
  dp: number | null,
  years: number | null,
  freq: "monthly" | "quarterly" | null,
  dpay: number | null,
  maint: number | null,
  title: string,
  unitType: string,
  beds: number
): Listing {
  return {
    listing_id: id,
    source_url: `https://example.invalid/demo/${id}`,
    collected_at: "2026-11-20T10:00:00+02:00",
    collected_by: "demo",
    verified_by: "demo",
    area,
    developer,
    price_egp: price,
    area_sqm: sqm,
    delivery_date: delivery,
    down_payment_pct: dp,
    years,
    frequency: freq,
    delivery_payment_pct: dpay,
    maintenance_pct: maint,
    notes: "بيانات تجريبية للعرض فقط.",
    title,
    unit_type: unitType,
    bedrooms: beds,
    image_urls: null,
    image_credit: null,
  };
}

let cache: MockState | null = null;

export function emptySlots(): MockSlots {
  return {
    areas: null,
    down_payment_available_egp: null,
    monthly_capacity_egp: null,
    timeline: null,
    purpose: null,
  };
}

function freshState(): MockState {
  const now = new Date().toISOString();
  return {
    version: 3,
    seq: 1000,
    users: [
      {
        user_id: "u_broker_1",
        email: "broker@aqar.demo",
        name: "سارة (وسيط تجريبي)",
        role: "broker",
        password: "broker123",
        created_at: now,
      },
      {
        user_id: "u_customer_1",
        email: "demo@aqar.demo",
        name: "عميل تجريبي",
        role: "customer",
        password: "demo1234",
        created_at: now,
      },
    ],
    conversations: [],
    views: {},
    latencies: [],
  };
}

export function loadState(): MockState {
  if (typeof window === "undefined") return cache ?? freshState();
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as MockState;
      if (parsed.version === 3) {
        cache = parsed;
        return parsed;
      }
    }
  } catch {
    // storage blocked: fall back to memory
  }
  if (!cache) cache = freshState();
  return cache;
}

export function saveState(state: MockState): void {
  cache = state;
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    // ignore: memory copy still works in this tab
  }
}

export function resetDemo(): void {
  cache = null;
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(KEY);
  } catch {
    // ignore
  }
}

export function nextId(state: MockState, prefix: string): string {
  state.seq += 1;
  return `${prefix}${state.seq}`;
}
