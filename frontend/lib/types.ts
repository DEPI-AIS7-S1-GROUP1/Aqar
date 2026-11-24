export type Mode = "AI_ACTIVE" | "HANDOFF_PENDING" | "HUMAN_ACTIVE" | "CLOSED";

export type Band = "cold" | "warm" | "hot";

export type Intent =
  | "search"
  | "info"
  | "compare"
  | "visit_or_reserve"
  | "human_request"
  | "objection"
  | "off_topic";

export type Timeline = "0-3m" | "3-12m" | "12m+" | "unknown";

export type Purpose = "live" | "invest";

export type AffordabilityStatus = "fit" | "tight" | "not_fit" | "unknown";

export interface MatchedUnit {
  listing_id: string;
  plan_id: string;
  affordability: AffordabilityStatus;
  liked?: boolean | null;
  title?: string;
  price_egp?: number;
  plan_summary?: string;
}

export interface ConfirmedSlots {
  areas?: string[] | null;
  down_payment_available_egp?: number | null;
  monthly_capacity_egp?: number | null;
  timeline?: Timeline | null;
  purpose?: Purpose | null;
}

export interface LeadBrief {
  lead_id: string;
  trigger: string;
  band: Band;
  score: number;
  reasons: string[];
  confirmed: ConfirmedSlots;
  unconfirmed: string[];
  matched_units: MatchedUnit[];
  open_questions: string[];
  summary_text?: string | null;
  transcript_url?: string | null;
  mode?: Mode;
}

export interface LeadSummary {
  lead_id: string;
  score: number;
  band: Band;
  main_interest: string;
  time_since_last_message: string;
  mode?: Mode;
}

export interface ChatMessage {
  id: string;
  role: "customer" | "user" | "assistant";
  content: string;
  timestamp?: string;
  unit?: {
    price_egp: number;
    plan_summary: string;
    affordability: AffordabilityStatus;
    title?: string;
  };
}
