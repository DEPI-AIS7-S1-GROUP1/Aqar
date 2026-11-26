// DEMO-ONLY fake of the FastAPI routes in Appendix B. Same paths, same shapes, same error envelope.
import type {
  AnalyticsResult,
  AuthResponse,
  Band,
  ChatMessage,
  CompareResult,
  ConversationView,
  LeadBrief,
  LeadSummary,
  ListingPage,
  UnitCard,
  User,
} from "@/lib/types";
import { AREAS } from "@/lib/format";
import {
  emptySlots,
  loadState,
  LISTINGS,
  nextId,
  saveState,
  type MockConversation,
  type MockState,
  type MockUser,
  type StoredMessage,
} from "./db";
import { GREETING, mainInterest, nextMissing, rescore, runTurn } from "./agent";
import { buildPlan, checkAffordability } from "./finance";

export class MockHttpError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

const fail = (status: number, code: string, message: string): never => {
  throw new MockHttpError(status, code, message);
};

function publicUser(u: MockUser): User {
  return { user_id: u.user_id, email: u.email, name: u.name, role: u.role, created_at: u.created_at };
}

function authResponse(state: MockState, u: MockUser): AuthResponse {
  const hasConv = state.conversations.some((c) => c.user_id === u.user_id);
  return {
    access_token: `mock.${u.user_id}`,
    token_type: "bearer",
    user: publicUser(u),
    is_new: u.role === "customer" && !hasConv,
  };
}

function currentUser(state: MockState, token: string | null): MockUser {
  const id = token?.startsWith("mock.") ? token.slice(5) : null;
  const u = state.users.find((x) => x.user_id === id);
  if (!u) fail(401, "unauthorized", "لازم تسجل دخول الأول.");
  return u!;
}

function requireRole(u: MockUser, role: "customer" | "broker") {
  if (u.role !== role) fail(403, "forbidden", "الصفحة دي مش متاحة لحسابك.");
}

function cardFor(conv: MockConversation | null, listingId: string, rate: number | null = null): UnitCard | null {
  const listing = LISTINGS.find((l) => l.listing_id === listingId);
  if (!listing) return null;
  const plan = buildPlan(listing, rate);
  const s = conv?.slots;
  const affordability =
    s && (s.down_payment_available_egp !== null || s.monthly_capacity_egp !== null)
      ? checkAffordability(plan, s.down_payment_available_egp, s.monthly_capacity_egp)
      : null;
  return { listing, plan, affordability };
}

function toChat(conv: MockConversation, m: StoredMessage): ChatMessage {
  return {
    message_id: m.message_id,
    role: m.role,
    text: m.text,
    created_at: m.created_at,
    cards: m.card_listing_ids.map((id) => cardFor(conv, id)).filter((c): c is UnitCard => c !== null),
  };
}

function view(conv: MockConversation, after: string | null = null): ConversationView {
  let msgs = conv.messages;
  if (after) {
    const i = msgs.findIndex((m) => m.message_id === after);
    msgs = i >= 0 ? msgs.slice(i + 1) : msgs;
  }
  return { conversation_id: conv.conversation_id, mode: conv.mode, messages: msgs.map((m) => toChat(conv, m)) };
}

function addMsg(state: MockState, conv: MockConversation, role: StoredMessage["role"], text: string, cards: string[] = []) {
  const m: StoredMessage = {
    message_id: nextId(state, "m"),
    role,
    text,
    created_at: new Date().toISOString(),
    card_listing_ids: cards,
  };
  conv.messages.push(m);
  conv.updated_at = m.created_at;
  return m;
}

function newConversation(state: MockState, userId: string): MockConversation {
  const conv: MockConversation = {
    conversation_id: nextId(state, "c"),
    lead_id: "",
    user_id: userId,
    mode: "AI_ACTIVE",
    messages: [],
    slots: emptySlots(),
    score: 0,
    band: "cold",
    reasons: [],
    shown: [],
    statuses: {},
    liked: {},
    visit_requested: false,
    trigger: null,
    taken_by: null,
    updated_at: new Date().toISOString(),
  };
  conv.lead_id = conv.conversation_id.replace("c", "");
  addMsg(state, conv, "ai", GREETING);
  state.conversations.push(conv);
  return conv;
}

function customerTurn(state: MockState, conv: MockConversation, text: string) {
  addMsg(state, conv, "user", text);
  if (conv.mode !== "AI_ACTIVE") return; // AI stays silent after handoff/takeover
  const res = runTurn(conv, text);
  for (const m of res.messages) addMsg(state, conv, "ai", m.text, m.cards);
  if (res.handoffTrigger) {
    conv.mode = "HANDOFF_PENDING";
    conv.trigger = res.handoffTrigger;
  }
}

/** A few scripted demo customers so the broker dashboard is not empty. */
function ensureSeed(state: MockState) {
  if (state.conversations.length > 0) return;
  const scripts: string[][] = [
    ["عايز شقة في التجمع", "معايا مقدم مليون", "القسط ميزيدش عن 50 ألف", "عايز أشتري الشهر ده", "للسكن", "أقدر أشوفها السبت؟"],
    ["بدور على حاجة في زايد", "مقدم 2 مليون", "قسط 150 ألف في الشهر", "خلال سنة", "استثمار"],
    ["العاصمة الإدارية", "مقدم 300 ألف", "القسط 25 ألف"],
    ["عايز أكلم حد من الفريق بخصوص أكتوبر"],
    ["بس بسأل على أسعار الساحل"],
  ];
  const base = Date.now();
  scripts.forEach((lines, i) => {
    const uid = `u_seed_${i}`;
    state.users.push({
      user_id: uid,
      email: `seed${i}@aqar.demo`,
      name: "عميل تجريبي",
      role: "customer",
      password: "seed",
      created_at: new Date(base).toISOString(),
    });
    const conv = newConversation(state, uid);
    lines.forEach((t) => customerTurn(state, conv, t));
    const ago = [12, 55, 180, 300, 1500][i] * 60000;
    const t0 = base - ago - conv.messages.length * 40000;
    conv.messages.forEach((m, k) => (m.created_at = new Date(t0 + k * 40000).toISOString()));
    conv.updated_at = conv.messages[conv.messages.length - 1].created_at;
  });
  state.views = { "NC-101": 14, "SZ-201": 9, "NA-401": 7, "OC-301": 5, "NCO-601": 4 };
}

function summary(c: MockConversation): LeadSummary {
  return {
    lead_id: c.lead_id,
    conversation_id: c.conversation_id,
    score: c.score,
    band: c.band,
    mode: c.mode,
    main_interest: mainInterest(c.slots),
    last_message_at: c.updated_at,
  };
}

const SLOT_QUESTIONS: Record<string, string> = {
  areas: "العميل بيدور في أنهي منطقة؟",
  down_payment_available_egp: "المقدم المتاح قد إيه؟",
  monthly_capacity_egp: "القسط الشهري المريح قد إيه؟",
  timeline: "ناوي يشتري إمتى؟",
  purpose: "سكن ولا استثمار؟",
};

function brief(c: MockConversation): LeadBrief {
  const s = c.slots;
  const unconfirmed = (Object.keys(SLOT_QUESTIONS) as (keyof typeof s)[]).filter((k) => s[k] === null);
  const matched = c.shown.map((id) => ({
    listing_id: id,
    plan_id: `P-${id}`,
    affordability: c.statuses[id] ?? "unknown",
    liked: c.liked[id] ?? null,
  }));
  const open = unconfirmed.map((k) => SLOT_QUESTIONS[k]);
  if (matched.some((m) => LISTINGS.find((l) => l.listing_id === m.listing_id)?.maintenance_pct === null))
    open.push("نسبة الصيانة مش منشورة لوحدة من الوحدات المقترحة.");
  const interest = mainInterest(s);
  const summaryText = interest
    ? `العميل بيدور على: ${interest}. اتعرض عليه ${matched.length.toLocaleString("ar-EG")} وحدات. ${
        c.trigger ? "طلب التواصل مع الفريق." : "لسه بيتأهل مع المساعد."
      }`
    : null;
  return {
    lead_id: c.lead_id,
    trigger: c.trigger ?? "in_progress",
    band: c.band,
    score: c.score,
    reasons: c.reasons,
    confirmed: { ...s },
    unconfirmed,
    matched_units: matched,
    open_questions: open,
    summary_text: summaryText,
    transcript_url: `/broker/leads/${c.lead_id}`,
  };
}

function leadByid(state: MockState, id: string): MockConversation {
  const c = state.conversations.find((x) => x.lead_id === id);
  if (!c) fail(404, "not_found", "العميل مش موجود.");
  return c!;
}

export async function mockRequest<T>(
  method: string,
  path: string,
  body: unknown,
  token: string | null
): Promise<T> {
  const started = performance.now();
  await new Promise((r) => setTimeout(r, 250 + Math.random() * 450));
  const state = loadState();
  ensureSeed(state);
  const url = new URL(path, "http://mock.local");
  const p = url.pathname.replace(/\/+$/, "");
  const q = url.searchParams;
  const b = (body ?? {}) as Record<string, unknown>;
  let result: unknown;
  let seg: RegExpMatchArray | null;

  if (method === "POST" && p === "/auth/signup") {
    const email = String(b.email ?? "").trim().toLowerCase();
    if (!email.includes("@")) fail(422, "validation_error", "اكتب إيميل صحيح.");
    if (String(b.password ?? "").length < 8) fail(422, "validation_error", "كلمة السر لازم 8 حروف على الأقل.");
    if (state.users.some((u) => u.email === email)) fail(409, "conflict", "الإيميل ده متسجل قبل كده. جرّب تسجيل الدخول.");
    const u: MockUser = {
      user_id: nextId(state, "u"),
      email,
      name: String(b.name ?? "").trim() || "عميل",
      role: "customer",
      password: String(b.password),
      created_at: new Date().toISOString(),
    };
    state.users.push(u);
    result = authResponse(state, u);
  } else if (method === "POST" && p === "/auth/login") {
    const email = String(b.email ?? "").trim().toLowerCase();
    let u = state.users.find((x) => x.email === email);
    if (!u) {
      // Demo convenience: unknown emails get an account. "broker" in the email = broker role.
      if (!email.includes("@")) fail(401, "unauthorized", "الإيميل أو كلمة السر غلط.");
      u = {
        user_id: nextId(state, "u"),
        email,
        name: email.includes("broker") ? "وسيط تجريبي" : email.split("@")[0],
        role: email.includes("broker") ? "broker" : "customer",
        password: String(b.password ?? ""),
        created_at: new Date().toISOString(),
      };
      state.users.push(u);
    } else if (u.password !== String(b.password ?? "")) {
      fail(401, "unauthorized", "الإيميل أو كلمة السر غلط.");
    }
    result = authResponse(state, u!);
  } else if (method === "GET" && p === "/auth/me") {
    result = publicUser(currentUser(state, token));
  } else if (method === "GET" && p === "/areas") {
    result = AREAS.map((a) => a.key);
  } else if (method === "GET" && p === "/listings") {
    const area = q.get("area");
    const minP = q.get("min_price") ? Number(q.get("min_price")) : null;
    const maxP = q.get("max_price") ? Number(q.get("max_price")) : null;
    const before = q.get("delivery_before");
    const beds = q.get("bedrooms_min") ? Number(q.get("bedrooms_min")) : null;
    const limit = Math.min(50, Number(q.get("limit") ?? 12));
    const offset = Number(q.get("offset") ?? 0);
    if (minP !== null && maxP !== null && minP > maxP) fail(422, "validation_error", "أقل سعر لازم يكون أصغر من أعلى سعر.");
    const items = LISTINGS.filter(
      (l) =>
        (!area || l.area === area) &&
        (minP === null || l.price_egp >= minP) &&
        (maxP === null || l.price_egp <= maxP) &&
        (!before || (l.delivery_date !== null && l.delivery_date <= before)) &&
        (beds === null || (l.bedrooms !== null && l.bedrooms >= beds))
    ).sort((a, c) => a.price_egp - c.price_egp);
    result = { items: items.slice(offset, offset + limit), total: items.length, limit, offset } satisfies ListingPage;
  } else if (method === "GET" && (seg = p.match(/^\/listings\/([^/]+)\/plans$/))) {
    const l = LISTINGS.find((x) => x.listing_id === seg![1]) ?? fail(404, "not_found", "الوحدة مش موجودة.");
    const rate = q.get("annual_discount_rate_pct");
    result = [buildPlan(l, rate ? Number(rate) : null)];
  } else if (method === "GET" && (seg = p.match(/^\/listings\/([^/]+)$/))) {
    result = LISTINGS.find((x) => x.listing_id === seg![1]) ?? fail(404, "not_found", "الوحدة مش موجودة.");
  } else if (method === "POST" && p === "/compare") {
    const ids = (b.listing_ids as string[]) ?? [];
    if (ids.length < 2 || ids.length > 3) fail(422, "validation_error", "اختار وحدتين أو تلاتة للمقارنة.");
    const rate = typeof b.annual_discount_rate_pct === "number" ? b.annual_discount_rate_pct : null;
    let conv: MockConversation | null = null;
    try {
      const u = currentUser(state, token);
      conv = state.conversations.find((c) => c.user_id === u.user_id) ?? null;
    } catch {
      conv = null;
    }
    const items = ids.map((id) => cardFor(conv, id, rate) ?? fail(404, "not_found", "وحدة مش موجودة."));
    result = { items } satisfies CompareResult;
  } else if (method === "POST" && p === "/events/listing-view") {
    const id = String(b.listing_id ?? "");
    state.views[id] = (state.views[id] ?? 0) + 1;
    result = null;
  } else if (method === "GET" && p === "/conversations/mine") {
    const u = currentUser(state, token);
    requireRole(u, "customer");
    const c = state.conversations.find((x) => x.user_id === u.user_id) ?? fail(404, "not_found", "مفيش محادثة لسه.");
    result = view(c);
  } else if (method === "POST" && p === "/conversations") {
    const u = currentUser(state, token);
    requireRole(u, "customer");
    const existing = state.conversations.find((x) => x.user_id === u.user_id);
    result = view(existing ?? newConversation(state, u.user_id));
  } else if (method === "POST" && (seg = p.match(/^\/conversations\/([^/]+)\/messages$/))) {
    const u = currentUser(state, token);
    requireRole(u, "customer");
    const c = state.conversations.find((x) => x.conversation_id === seg![1] && x.user_id === u.user_id) ?? fail(404, "not_found", "المحادثة مش موجودة.");
    const text = String(b.text ?? "").trim();
    if (!text) fail(422, "validation_error", "الرسالة فاضية.");
    const lastId = c.messages[c.messages.length - 1].message_id;
    customerTurn(state, c, text);
    result = view(c, lastId);
  } else if (method === "GET" && (seg = p.match(/^\/conversations\/([^/]+)$/))) {
    const u = currentUser(state, token);
    const c = state.conversations.find((x) => x.conversation_id === seg![1]) ?? fail(404, "not_found", "المحادثة مش موجودة.");
    if (u.role === "customer" && c.user_id !== u.user_id) fail(403, "forbidden", "المحادثة دي مش بتاعتك.");
    result = view(c, q.get("after"));
  } else if (p.startsWith("/broker")) {
    const u = currentUser(state, token);
    requireRole(u, "broker");
    if (method === "GET" && p === "/broker/leads") {
      const band = q.get("band") as Band | null;
      result = state.conversations
        .filter((c) => c.messages.some((m) => m.role === "user"))
        .filter((c) => !band || c.band === band)
        .map(summary)
        .sort((a, c) => c.score - a.score);
    } else if (method === "GET" && p === "/broker/analytics") {
      const leads = state.conversations.filter((c) => c.messages.some((m) => m.role === "user"));
      const byBand: Record<string, number> = { hot: 0, warm: 0, cold: 0 };
      const areas: Record<string, number> = {};
      leads.forEach((c) => {
        byBand[c.band] += 1;
        c.slots.areas?.forEach((a) => (areas[a] = (areas[a] ?? 0) + 1));
      });
      const lat = state.latencies.slice().sort((a, c) => a - c);
      result = {
        leads_by_band: byBand,
        top_areas: Object.entries(areas).map(([key, count]) => ({ key, count })).sort((a, c) => c.count - a.count),
        top_listings: Object.entries(state.views).map(([key, count]) => ({ key, count })).sort((a, c) => c.count - a.count).slice(0, 5),
        p95_latency_ms: lat.length ? Math.round(lat[Math.floor(lat.length * 0.95)] ?? lat[lat.length - 1]) : null,
        cache_hit_rate: null,
      } satisfies AnalyticsResult;
    } else if ((seg = p.match(/^\/broker\/leads\/([^/]+)(?:\/(takeover|messages|release|close))?$/))) {
      const c = leadByid(state, seg[1]);
      const action = seg[2];
      if (method === "GET" && !action) result = brief(c);
      else if (method === "POST" && action === "takeover") {
        if (c.mode === "HUMAN_ACTIVE") fail(409, "conflict", "في وسيط تاني استلم العميل ده.");
        if (c.mode === "CLOSED") fail(409, "conflict", "العميل ده مقفول.");
        c.mode = "HUMAN_ACTIVE";
        c.taken_by = u.user_id;
        addMsg(state, c, "system", "انضم مستشار من الفريق للمحادثة.");
        result = view(c);
      } else if (method === "POST" && action === "messages") {
        if (c.mode !== "HUMAN_ACTIVE") fail(409, "conflict", "لازم تستلم المحادثة الأول.");
        const text = String(b.text ?? "").trim() || fail(422, "validation_error", "الرسالة فاضية.");
        result = toChat(c, addMsg(state, c, "broker", text as string));
      } else if (method === "POST" && action === "release") {
        c.mode = "AI_ACTIVE";
        c.taken_by = null;
        addMsg(state, c, "system", "رجعت المحادثة للمساعد.");
        const next = nextMissing(c.slots);
        if (next) addMsg(state, c, "ai", "أنا رجعت معاك تاني. نكمل من حيث وقفنا؟");
        result = view(c);
      } else if (method === "POST" && action === "close") {
        c.mode = "CLOSED";
        addMsg(state, c, "system", "تم قفل المحادثة.");
        result = summary(c);
      } else fail(404, "not_found", "المسار مش موجود.");
    } else fail(404, "not_found", "المسار مش موجود.");
  } else {
    fail(404, "not_found", "المسار مش موجود.");
  }

  state.conversations.forEach((c) => {
    if (c.messages.length > 1 && c.reasons.length === 0) rescore(c);
  });
  state.latencies = [...state.latencies.slice(-199), performance.now() - started];
  saveState(state);
  return result as T;
}
