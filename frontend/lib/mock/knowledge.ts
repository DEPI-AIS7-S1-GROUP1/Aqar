// DEMO-ONLY stand-in for the real RAG (backend/app/rag). Answers questions about an area or a
// developer from the same guides (data/docs), copied into guides.ts by scripts/build_mock_guides.py.
// Real mode: the agent calls get_rag().search() and sends the hits' sources with the reply.
import type { SourceRef } from "@/lib/types";
import { GUIDE_SECTIONS, type GuideSection } from "./guides";

const ENTITIES: [RegExp, string][] = [
  // developers first: "Mountain View Hyde Park" is a project, so the developer wins
  [/سوديك|sodic/i, "sodic"],
  [/بالم هيلز|palm ?hills/i, "palm_hills"],
  [/ماونتن فيو|ماونتين فيو|mountain ?view|\bdmg\b/i, "mountain_view"],
  [/هايد بارك|hyde ?park/i, "hyde_park"],
  [/تطوير مصر|tatweer/i, "tatweer_misr"],
  [/سيتي [اإ]يدج|city ?edge/i, "city_edge"],
  [/[اأ]وراسكوم|orascom|o ?west|الجونه|الجونة/i, "orascom"],
  [/طلعت مصطفى|\btmg\b|مدينتي|الرحاب/i, "tmg"],
  // areas
  [/التجمع|القاهره الجديده|القاهرة الجديدة|new cairo|tagamo/i, "new_cairo"],
  [/زايد|zayed/i, "sheikh_zayed"],
  [/[اأ]كتوبر|october/i, "october_6"],
  [/العاصمه|العاصمة|capital/i, "new_capital"],
  [/مستقبل سيتي|مدينة المستقبل|mostakbal/i, "mostakbal_city"],
  [/المعادي|معادي|maadi/i, "maadi"],
];

// which section answers which kind of question (matched against the heading)
const TOPICS: [RegExp, RegExp][] = [
  [/تسليم|بيسلم|بتسلم|سلّم|سلم|ملتزم|موثوق|مضمون|سمع[ةه]|تأخير|اتأخر/, /سجل التسليم/],
  [/مواصلات|مترو|مونوريل|قطر|طريق|طرق|محور|توصل|[اأ]وصل|بعيد|المساف[ةه]/, /المواصلات/],
  [/مدارس|مدرس[ةه]|جامع[ةه]|جامعات|مستشف|خدمات|مول|مولات|نادي/, /الخدمات/],
  [/مناسب|عيل[ةه]|عائل|[اأ]طفال|ولاد|شباب|[اأ]سكن|استثمار|كويس[ةه]? ل/, /مناسبة لمين/],
  [/مشروع|مشاريع|كمبوند|بيبني|بتبني|سكن/, /السكن والمشروعات|أهم المشروعات/],
];

// is this a question about a place or a company, not an answer to our own questions?
const ASKING =
  /[؟?]|كويس|[اإ]زاي|(^|\s)([اإ]يه|فين|مين)(\s|$)|تعرف|احكيلي|قولي عن|معلومات|مناسب|سمع[ةه]|موثوق|مضمون|بيسلم|اتأسس/;

export interface KnowledgeAnswer {
  text: string;
  sources: SourceRef[];
}

function shortTitle(s: GuideSection): string {
  return s.title.replace(/\s*\(.*?\)\s*/g, "").trim();
}

function pick(entity: string, text: string): GuideSection | null {
  const sections = GUIDE_SECTIONS.filter((s) => s.entity_id === entity);
  if (!sections.length) return null;
  for (const [ask, heading] of TOPICS) {
    if (!ask.test(text)) continue;
    const hit = sections.find((s) => heading.test(s.heading));
    if (hit) return hit;
  }
  return sections[0];
}

/** An answer from the guides, or null when the message is not a question about an area/developer. */
export function answerFromGuides(text: string, hasAmounts: boolean): KnowledgeAnswer | null {
  if (hasAmounts || !ASKING.test(text)) return null;
  const entities = ENTITIES.filter(([re]) => re.test(text)).map(([, id]) => id);
  const unique = Array.from(new Set(entities)).slice(0, 2);
  const parts: string[] = [];
  const sources: SourceRef[] = [];
  for (const id of unique) {
    const s = pick(id, text);
    if (!s) continue;
    parts.push(`عن ${shortTitle(s)}: ${s.text}`);
    if (!sources.some((x) => x.url === s.source.url)) sources.push(s.source);
  }
  if (!parts.length) return null;
  return { text: parts.join("\n\n"), sources };
}
