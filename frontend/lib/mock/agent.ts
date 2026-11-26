// DEMO-ONLY scripted assistant that behaves like the real LangGraph agent (Member 4)
// closely enough to click through the whole flow without a backend.
// Scoring follows the architecture table; numbers only come from the customer or the mock calculator.
import type { AffordabilityStatus, Band } from "@/lib/types";
import { AREAS, areaLabel, formatEgp, TIMELINE_LABEL, PURPOSE_LABEL } from "@/lib/format";
import { LISTINGS, type MockConversation, type MockSlots } from "./db";
import { buildPlan, checkAffordability } from "./finance";

export const GREETING =
  "أهلاً بيك في عقار! أنا مساعدك العقاري. هسألك كام سؤال بسيط عشان أرشحلك وحدات تقدر عليها فعلاً. بتدور على وحدة في أنهي منطقة؟";

export const HANDOFF_TEXT = "هوصلك بمستشار من الفريق خلال دقايق.";

const AREA_WORDS: [RegExp, string][] = [
  [/التجمع|القاهره الجديده|القاهرة الجديدة|new cairo|tagamo/i, "new_cairo"],
  [/زايد|zayed/i, "sheikh_zayed"],
  [/اكتوبر|أكتوبر|october/i, "october_6"],
  [/العاصمه|العاصمة|capital/i, "new_capital"],
  [/مستقبل|mostakbal/i, "mostakbal_city"],
  [/الساحل|راس الحكمه|رأس الحكمة|راس الحكمة|north coast|sahel/i, "north_coast_ras_el_hekma"],
];

function toLatinDigits(s: string): string {
  return s
    .replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
    .replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06f0))
    .replace(/[٬،,](?=\d{3})/g, "")
    .replace(/٫/g, ".");
}

interface Amount {
  value: number;
  index: number;
}

export function parseAmounts(raw: string): Amount[] {
  let text = toLatinDigits(raw);
  const out: Amount[] = [];
  const take = (re: RegExp, fn: (m: RegExpExecArray) => number) => {
    let m: RegExpExecArray | null;
    const g = new RegExp(re.source, re.flags.includes("g") ? re.flags : re.flags + "g");
    while ((m = g.exec(text)) !== null) {
      out.push({ value: fn(m), index: m.index });
      text = text.slice(0, m.index) + " ".repeat(m[0].length) + text.slice(m.index + m[0].length);
      g.lastIndex = 0;
    }
  };
  take(/مليون\s*و\s*نص|مليون\s*ونص/, () => 1_500_000);
  take(/نص\s*مليون/, () => 500_000);
  take(/ربع\s*مليون/, () => 250_000);
  take(/(\d+(?:\.\d+)?)\s*(?:مليون|million|m\b)/i, (m) => parseFloat(m[1]) * 1_000_000);
  take(/مليونين/, () => 2_000_000);
  take(/(\d+(?:\.\d+)?)\s*(?:ألف|الف|آلاف|الاف|k\b)/i, (m) => parseFloat(m[1]) * 1_000);
  take(/مليون/, () => 1_000_000);
  take(/\d{4,}/, (m) => parseFloat(m[0]));
  return out.sort((a, b) => a.index - b.index);
}

type Pending = "areas" | "down" | "monthly" | "timeline" | "purpose" | null;

export function nextMissing(s: MockSlots): Pending {
  if (!s.areas) return "areas";
  if (s.down_payment_available_egp === null) return "down";
  if (s.monthly_capacity_egp === null) return "monthly";
  if (!s.timeline) return "timeline";
  if (!s.purpose) return "purpose";
  return null;
}

const QUESTIONS: Record<Exclude<Pending, null>, string> = {
  areas: "بتدور في أنهي منطقة؟ (مثلاً التجمع، زايد، أكتوبر، العاصمة، مستقبل سيتي، الساحل)",
  down: "تمام. معاك مقدم قد إيه تقريبًا؟",
  monthly: "والقسط اللي يريحك في الشهر يكون حوالي كام؟",
  timeline: "وناوي تشتري إمتى؟ قريب خلال كام شهر، ولا خلال سنة، ولا مش مستعجل؟",
  purpose: "وآخر سؤال: الوحدة للسكن ولا للاستثمار؟",
};

export interface TurnResult {
  messages: { text: string; cards: string[] }[];
  handoffTrigger: string | null;
}

export function runTurn(conv: MockConversation, userText: string): TurnResult {
  const text = userText.trim();
  const s = conv.slots;
  const pendingBefore = nextMissing(s);
  const captured: string[] = [];
  const hadCore = Boolean(s.areas && s.down_payment_available_egp !== null && s.monthly_capacity_egp !== null);

  // areas
  const areas = AREA_WORDS.filter(([re]) => re.test(text)).map(([, k]) => k);
  if (areas.length) {
    s.areas = Array.from(new Set(areas));
    captured.push(`المنطقة: ${s.areas.map(areaLabel).join("، ")}`);
  }

  // amounts
  const amounts = parseAmounts(text);
  const lt = toLatinDigits(text);
  for (const a of amounts) {
    const before = lt.slice(Math.max(0, a.index - 25), a.index);
    const after = lt.slice(a.index, a.index + 25);
    let slot: "down" | "monthly" | null = null;
    if (/مقدم|مقدّم|down/i.test(before) || /مقدم/.test(after)) slot = "down";
    else if (/قسط|شهر|شهري|monthly/i.test(before + after)) slot = "monthly";
    else if (pendingBefore === "down" || pendingBefore === "monthly") slot = pendingBefore;
    else if (s.down_payment_available_egp === null) slot = "down";
    else if (s.monthly_capacity_egp === null) slot = "monthly";
    if (slot === "down") {
      s.down_payment_available_egp = a.value;
      captured.push(`مقدم ${formatEgp(a.value)}`);
    } else if (slot === "monthly") {
      s.monthly_capacity_egp = a.value;
      captured.push(`قسط ${formatEgp(a.value)} في الشهر`);
    }
  }

  // timeline
  if (/الشهر ده|قريب|فورا|فوراً|حالا|حالاً|خلال شهر|الشهر الجاي|asap/i.test(text)) s.timeline = "0-3m";
  else if (/خلال سنه|خلال سنة|السنه دي|السنة دي|كام شهر|6 شهور|ست شهور/.test(text)) s.timeline = "3-12m";
  else if (/مش مستعجل|سنتين|بعد سنه|بعد سنة|لسه بدري/.test(text)) s.timeline = "12m+";
  else if (pendingBefore === "timeline" && /مش عارف|مش متأكد/.test(text)) s.timeline = "unknown";
  if (s.timeline && pendingBefore === "timeline") captured.push(`التوقيت: ${TIMELINE_LABEL[s.timeline]}`);

  // purpose
  if (/سكن|اسكن|أسكن|اعيش|أعيش|عيلتي|live/i.test(text)) s.purpose = "live";
  else if (/استثمار|استثمر|أستثمر|ايجار|إيجار|invest/i.test(text)) s.purpose = "invest";
  if (s.purpose && pendingBefore === "purpose") captured.push(`الغرض: ${PURPOSE_LABEL[s.purpose]}`);

  // intents
  const wantsHuman = /اكلم حد|أكلم حد|موظف|بني ادم|بني آدم|وسيط|سمسار|حد من الفريق|human|agent/i.test(text);
  const wantsVisit = /معاينه|معاينة|اعاين|أعاين|نعاين|اشوفها|أشوفها|نشوفها|اشوف الوحده|أشوف الوحدة|زياره|زيارة|احجز|أحجز|حجز|visit/i.test(text);
  const wantsCompare = /قارن|مقارنه|مقارنة|الفرق بين|compare/i.test(text);
  const sensitive = /خصم|عقد|قانون|محامي|discount|contract/i.test(text);

  const msgs: TurnResult["messages"] = [];
  const ack = captured.length ? `تمام، سجلت: ${captured.join("، ")}.` : "";

  if (wantsHuman || sensitive || wantsVisit) {
    conv.visit_requested = conv.visit_requested || wantsVisit;
    const trigger = wantsHuman ? "human_request" : sensitive ? "sensitive_topic" : "visit_or_reserve";
    if (ack) msgs.push({ text: ack, cards: [] });
    msgs.push({ text: HANDOFF_TEXT, cards: [] });
    rescore(conv);
    return { messages: msgs, handoffTrigger: trigger };
  }

  const hasCore = Boolean(s.areas && s.down_payment_available_egp !== null && s.monthly_capacity_egp !== null);

  // customer asks about a specific unit (from the unit page button)
  const idMatch = text.match(/\b([A-Z]{2,3}-\d{3})\b/);
  const asked = idMatch ? LISTINGS.find((l) => l.listing_id === idMatch[1]) : undefined;
  if (asked) {
    const aff = checkAffordability(buildPlan(asked), s.down_payment_available_egp, s.monthly_capacity_egp);
    if (aff.status !== "unknown") conv.statuses[asked.listing_id] = aff.status;
    conv.shown = Array.from(new Set([asked.listing_id, ...conv.shown]));
    if (!s.areas) s.areas = [asked.area];
    rescore(conv);
    const verdict =
      aff.status === "unknown"
        ? "عشان أقولك تناسبك ولا لأ محتاج أعرف المقدم والقسط اللي يريحوك."
        : `بالنسبة لحدودك: ${aff.reason}`;
    msgs.push({ text: `${ack} دي الوحدة اللي سألت عليها. ${verdict}`.trim(), cards: [asked.listing_id] });
    const next = nextMissing(s);
    if (next) msgs.push({ text: QUESTIONS[next], cards: [] });
    return { messages: msgs, handoffTrigger: null };
  }

  const coreChanged = hasCore && (!hadCore || amounts.length > 0 || areas.length > 0);

  if (hasCore && (coreChanged || conv.shown.length === 0)) {
    const ranked = match(conv);
    rescore(conv);
    if (ranked.length === 0) {
      msgs.push({ text: `${ack} للأسف مفيش وحدات عندنا دلوقتي في المنطقة دي. تحب أدورلك في منطقة تانية؟`.trim(), cards: [] });
    } else {
      const notFitAll = ranked.every((id) => conv.statuses[id] === "not_fit");
      const lead = notFitAll
        ? "دي أقرب الوحدات، بس بصراحة كلها أعلى من حدودك. ممكن نفكر في مقدم أعلى أو منطقة تانية:"
        : `لقيتلك ${ranked.length.toLocaleString("ar-EG")} وحدات مرتبة حسب قدرتك على الدفع:`;
      msgs.push({ text: `${ack} ${lead}`.trim(), cards: ranked });
      const next = nextMissing(s);
      if (next) msgs.push({ text: QUESTIONS[next], cards: [] });
      else msgs.push({ text: "تحب أقارنلك بين وحدتين؟ ولو حابب تشوف وحدة على الطبيعة قولي وأنا أرتبلك معاد.", cards: [] });
    }
    return { messages: msgs, handoffTrigger: null };
  }

  rescore(conv);
  if (wantsCompare && conv.shown.length >= 2) {
    msgs.push({ text: "دوس على «قارن الوحدات» تحت الكروت وهتلاقي الخطتين جنب بعض.", cards: conv.shown.slice(0, 2) });
    return { messages: msgs, handoffTrigger: null };
  }

  const next = nextMissing(s);
  if (next) {
    const lead = ack || (pendingBefore && !captured.length ? "معلش مش متأكد إني فهمت." : "");
    msgs.push({ text: `${lead} ${QUESTIONS[next]}`.trim(), cards: [] });
  } else {
    msgs.push({
      text: `${ack} تحب أعرضلك تفاصيل وحدة معينة أو أقارن بين وحدتين؟ ولو عايز تشوف وحدة على الطبيعة قولي وأنا أرتبلك معاد مع حد من الفريق.`.trim(),
      cards: [],
    });
  }
  return { messages: msgs, handoffTrigger: null };
}

const ORDER: Record<AffordabilityStatus, number> = { fit: 0, tight: 1, unknown: 2, not_fit: 3 };

function match(conv: MockConversation): string[] {
  const s = conv.slots;
  let pool = LISTINGS.filter((l) => s.areas?.includes(l.area));
  if (pool.length === 0) pool = LISTINGS.slice();
  const scored = pool.map((l) => {
    const plan = buildPlan(l);
    const aff = checkAffordability(plan, s.down_payment_available_egp, s.monthly_capacity_egp);
    conv.statuses[l.listing_id] = aff.status;
    return { id: l.listing_id, status: aff.status, price: l.price_egp };
  });
  scored.sort((a, b) => ORDER[a.status] - ORDER[b.status] || a.price - b.price);
  const top = scored.slice(0, 3).map((x) => x.id);
  conv.shown = Array.from(new Set([...top, ...conv.shown]));
  return top;
}

export function rescore(conv: MockConversation): void {
  const s = conv.slots;
  const reasons: string[] = [];
  let score = 0;
  const add = (pts: number, why: string) => {
    score += pts;
    reasons.push(`${why} (${pts > 0 ? "+" : ""}${pts})`);
  };
  if (s.timeline === "0-3m") add(30, "التوقيت خلال 3 شهور");
  else if (s.timeline === "3-12m") add(15, "التوقيت خلال سنة");
  if (s.down_payment_available_egp !== null) add(10, "المقدم المتاح معروف");
  if (s.monthly_capacity_egp !== null) add(10, "القسط المريح معروف");
  if (s.areas) add(5, "المنطقة متحددة");
  const statuses = conv.shown.map((id) => conv.statuses[id]).filter(Boolean);
  const best = statuses.sort((a, b) => ORDER[a] - ORDER[b])[0];
  if (best === "fit") add(25, "فيه وحدة مناسبة لقدرته");
  else if (best === "tight") add(10, "أقرب وحدة ضاغطة شوية");
  else if (best === "not_fit") add(-20, "الوحدات اللي اتعرضت مش مناسبة لقدرته");
  if (conv.visit_requested) add(20, "طلب معاينة أو حجز");
  score = Math.max(0, Math.min(100, score));
  let band: Band = score >= 70 ? "hot" : score >= 40 ? "warm" : "cold";
  if (band === "hot" && (best === "not_fit" || s.timeline === "12m+")) band = "warm";
  conv.score = score;
  conv.band = band;
  conv.reasons = reasons;
}

export function mainInterest(s: MockSlots): string | null {
  const parts: string[] = [];
  if (s.areas) parts.push(s.areas.map((a) => AREAS.find((x) => x.key === a)?.short ?? a).join(" / "));
  if (s.down_payment_available_egp !== null) parts.push(`مقدم ${formatEgp(s.down_payment_available_egp)}`);
  if (s.monthly_capacity_egp !== null) parts.push(`قسط ${formatEgp(s.monthly_capacity_egp)}`);
  if (s.purpose) parts.push(PURPOSE_LABEL[s.purpose]);
  return parts.length ? parts.join(" · ") : null;
}
