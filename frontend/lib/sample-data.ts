// REPLACE when the mock file exists
import { ChatMessage, LeadBrief, LeadSummary } from "./types";

export const SAMPLE_CONVERSATION: ChatMessage[] = [
  {
    id: "msg_1",
    role: "assistant",
    content:
      "أهلاً بحضرتك في AqarAI! أنا مساعدك العقاري الذكي بالعامية المصرية. بتدور على شقة أو وحدة في منطقة معينة في مصر؟",
    timestamp: "10:00 ص",
  },
  {
    id: "msg_2",
    role: "customer",
    content:
      "أهلاً، أنا بدور على شقة في New Cairo بمقدم 250,000 وقسط شهري ميزيدش عن 30,000 جنيه.",
    timestamp: "10:01 ص",
  },
  {
    id: "msg_3",
    role: "assistant",
    content:
      "تمام جداً! الميزانية دي ممتازة ومناسبة لمنطقة New Cairo بمقدم 250,000 وقسط 30,000 شهرياً. لقيتلك وحدة مطابقة تماماً للميزانية دي:",
    timestamp: "10:02 ص",
    unit: {
      price_egp: 3000000,
      plan_summary:
        "مقدم 250,000 ج.م وقسط شهري 28,500 ج.م على 8 سنوات بدون فوائد",
      affordability: "fit",
      title: "شقة 160م تشطيب كامل كمبوند في New Cairo",
    },
  },
  {
    id: "msg_4",
    role: "customer",
    content: "ممتاز جداً، هل الوحدة دي استلام فوري ولا تحت الإنشاء؟",
    timestamp: "10:03 ص",
  },
];

export const SAMPLE_LEADS: LeadSummary[] = [
  {
    lead_id: "1042",
    score: 92,
    band: "hot",
    main_interest: "شقة 3 غرف في New Cairo بمقدم 250,000",
    time_since_last_message: "منذ 15 دقيقة",
    mode: "AI_ACTIVE",
  },
  {
    lead_id: "1038",
    score: 85,
    band: "hot",
    main_interest: "تاون هاوس في الشيخ زايد استلام سنتين",
    time_since_last_message: "منذ ساعة",
    mode: "HANDOFF_PENDING",
  },
  {
    lead_id: "1025",
    score: 68,
    band: "warm",
    main_interest: "شقة استثمارية في العاصمة الإدارية",
    time_since_last_message: "منذ 3 ساعات",
    mode: "AI_ACTIVE",
  },
  {
    lead_id: "1019",
    score: 55,
    band: "warm",
    main_interest: "دوبلكس في الشروق بميزانية 5 مليون",
    time_since_last_message: "منذ 5 ساعات",
    mode: "AI_ACTIVE",
  },
  {
    lead_id: "1007",
    score: 38,
    band: "cold",
    main_interest: "استفسار عام عن أسعار الساحل الشمالي",
    time_since_last_message: "منذ يوم",
    mode: "CLOSED",
  },
  {
    lead_id: "1002",
    score: 24,
    band: "cold",
    main_interest: "بحث مبدئي بدون تحديد ميزانية أو مقدم",
    time_since_last_message: "منذ يومين",
    mode: "CLOSED",
  },
];

export const SAMPLE_LEAD_DETAILS: Record<string, LeadBrief> = {
  "1042": {
    lead_id: "1042",
    trigger: "العميل أكد الميزانية وطلب زيارة ميدانية في New Cairo",
    band: "hot",
    score: 92,
    reasons: [
      "تأكيد كامل لمقدم 250,000 وقسط 30,000 شهرياً",
      "المنطقة محددة بدقة (New Cairo)",
      "جاهزية عالية وموافقة على التواصل المباشر مع الوسيط",
    ],
    confirmed: {
      areas: ["New Cairo"],
      down_payment_available_egp: 250000,
      monthly_capacity_egp: 30000,
      timeline: "0-3m",
      purpose: "live",
    },
    unconfirmed: ["bedrooms_min", "delivery_date"],
    matched_units: [
      {
        listing_id: "unit_nc_204",
        plan_id: "plan_8y_std",
        affordability: "fit",
        liked: true,
        title: "شقة 160م تشطيب كامل كمبوند في New Cairo",
        price_egp: 3000000,
        plan_summary: "مقدم 250,000 وقسط شهري 28,500 على 8 سنوات",
      },
      {
        listing_id: "unit_nc_108",
        plan_id: "plan_7y_flex",
        affordability: "tight",
        liked: null,
        title: "شقة 140م استلام فوري التجمع الخامس",
        price_egp: 3400000,
        plan_summary: "مقدم 300,000 وقسط شهري 32,000 على 7 سنوات",
      },
    ],
    open_questions: [
      "هل يفضل العميل الدور الأرضي بحديقة أم الأدوار المتكررة؟",
      "تاريخ الزيارة المقترح لمعاينة الكمبوند على أرض الواقع",
    ],
    summary_text:
      "العميل مهتم جداً بشراء شقة سكنية في منطقة New Cairo، الميزانية واضحة بمقدم 250 ألف وقسط شهري حتى 30 ألف جنيه، جاهز للتعاقد خلال 3 أشهر وموافق على تحويل المحادثة للوسيط لترتيب موعد المعاينة.",
    transcript_url: "/chat",
    mode: "AI_ACTIVE",
  },
  "1038": {
    lead_id: "1038",
    trigger: "طلب موظف المبيعات مباشرة لحجز تاون هاوس",
    band: "hot",
    score: 85,
    reasons: [
      "ميزانية مرتفعة مؤكدة",
      "طلب معاينة فورية في الشيخ زايد",
    ],
    confirmed: {
      areas: ["الشيخ زايد"],
      down_payment_available_egp: 800000,
      monthly_capacity_egp: 75000,
      timeline: "3-12m",
      purpose: "live",
    },
    unconfirmed: [],
    matched_units: [
      {
        listing_id: "unit_zy_501",
        plan_id: "plan_6y_lux",
        affordability: "fit",
        liked: true,
        title: "تاون هاوس 220م كمبوند زايد ريزيدنس",
        price_egp: 7500000,
        plan_summary: "مقدم 800,000 وقسط 70,000 شهرياً على 6 سنوات",
      },
    ],
    open_questions: ["الموعد المفضل للمكالمة"],
    summary_text:
      "عميل جاد يبحث عن تاون هاوس استلام سنتين في الشيخ زايد، المقدم والأقساط متوافقة تماماً.",
    transcript_url: "/chat",
    mode: "HANDOFF_PENDING",
  },
  "1025": {
    lead_id: "1025",
    trigger: "استفسار استثماري مع رغبة في مقارنة العوائد",
    band: "warm",
    score: 68,
    reasons: ["ميزانية مقترحة بدون تأكيد نهائي", "هدف الشراء استثماري"],
    confirmed: {
      areas: ["العاصمة الإدارية"],
      down_payment_available_egp: 400000,
      monthly_capacity_egp: 35000,
      timeline: "3-12m",
      purpose: "invest",
    },
    unconfirmed: ["preferred_payment_plan"],
    matched_units: [
      {
        listing_id: "unit_cap_102",
        plan_id: "plan_10y_inv",
        affordability: "fit",
        liked: true,
        title: "وحدة فندقية بالعاصمة الإدارية",
        price_egp: 4200000,
        plan_summary: "مقدم 400,000 وقسط 35,000 شهرياً على 10 سنوات",
      },
    ],
    open_questions: ["هل يفضل العائد الإيجاري الإلزامي أم إعادة البيع؟"],
    summary_text:
      "مشتري بهدف الاستثمار في العاصمة الإدارية بمقدم حوالي 400 ألف وقسط 35 ألف، يفاضل بين خطط السداد الطويلة.",
    transcript_url: "/chat",
    mode: "AI_ACTIVE",
  },
  "1019": {
    lead_id: "1019",
    trigger: "مقارنة وحدات دوبلكس بالشروق",
    band: "warm",
    score: 55,
    reasons: ["تفضيل لمنطقة الشروق", "لم يؤكد القدرة على القسط بعد"],
    confirmed: {
      areas: ["الشروق"],
      down_payment_available_egp: 500000,
      monthly_capacity_egp: null,
      timeline: "12m+",
      purpose: "live",
    },
    unconfirmed: ["monthly_capacity_egp", "timeline"],
    matched_units: [
      {
        listing_id: "unit_sh_301",
        plan_id: "plan_8y_sh",
        affordability: "tight",
        liked: false,
        title: "دوبلكس 240م حي النخيل الشروق",
        price_egp: 5000000,
        plan_summary: "مقدم 500,000 وقسط 47,000 على 8 سنوات",
      },
    ],
    open_questions: ["الحد الأقصى للقسط الشهري المريح للعميل"],
    summary_text:
      "العميل يبحث عن دوبلكس في الشروق بمقدم 500 ألف، لكن لم يؤكد القسط الشهري المناسب بعد.",
    transcript_url: "/chat",
    mode: "AI_ACTIVE",
  },
  "1007": {
    lead_id: "1007",
    trigger: "استفسار مبكر عن مشروعات الصيف",
    band: "cold",
    score: 38,
    reasons: ["استفسار عام فقط", "لا توجد ميزانية مؤكدة"],
    confirmed: {
      areas: ["الساحل الشمالي"],
      down_payment_available_egp: null,
      monthly_capacity_egp: null,
      timeline: "unknown",
      purpose: null,
    },
    unconfirmed: [
      "down_payment_available_egp",
      "monthly_capacity_egp",
      "purpose",
    ],
    matched_units: [],
    open_questions: ["الميزانية التقريبية ومقدم الحجز المتاح"],
    summary_text:
      "استفسار عام عن أسعار الشاليهات بالساحل الشمالي دون توضيح الميزانية أو الجدية الحالية.",
    transcript_url: "/chat",
    mode: "CLOSED",
  },
  "1002": {
    lead_id: "1002",
    trigger: "طلب معلومات دون تفاصيل",
    band: "cold",
    score: 24,
    reasons: ["لم يتم تحديد منطقة أو ميزانية"],
    confirmed: {
      areas: null,
      down_payment_available_egp: null,
      monthly_capacity_egp: null,
      timeline: "unknown",
      purpose: null,
    },
    unconfirmed: ["areas", "down_payment", "monthly_capacity", "timeline"],
    matched_units: [],
    open_questions: ["أي منطقة يفضل العميل في مصر؟"],
    summary_text:
      "بحث أولي مبهم بدون أي متطلبات مؤكدة؛ بحاجة لإعادة استهداف لاحقاً.",
    transcript_url: "/chat",
    mode: "CLOSED",
  },
};

/**
 * Format any field value. Unknown (null/undefined/blank) shows 'غير متوفر', never 0 and never blank.
 */
export function formatValue(val: unknown): string {
  if (val === null || val === undefined || val === "") {
    return "غير متوفر";
  }
  if (Array.isArray(val)) {
    return val.length > 0 ? val.join("، ") : "غير متوفر";
  }
  if (typeof val === "number") {
    return val.toLocaleString("ar-EG");
  }
  return String(val);
}
