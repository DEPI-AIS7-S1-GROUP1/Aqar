// Mirrors backend/app/contracts.py (contracts-v2). Optional = null when unknown, never 0.

export type Mode = "AI_ACTIVE" | "HANDOFF_PENDING" | "HUMAN_ACTIVE" | "CLOSED";
export type Band = "cold" | "warm" | "hot";
export type Role = "customer" | "broker";
export type MessageRole = "user" | "ai" | "broker" | "system";

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
export type Frequency = "monthly" | "quarterly";

// ---------- Auth ----------
export interface User {
  user_id: string;
  email: string;
  name: string;
  role: Role;
  created_at: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
  phone: string | null;
  contact_consent: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
  is_new: boolean;
}

// ---------- Listings ----------
export interface Listing {
  listing_id: string;
  source_url: string;
  collected_at: string;
  collected_by: string;
  verified_by: string | null;
  area: string;
  developer: string;
  price_egp: number;
  area_sqm: number;
  delivery_date: string | null;
  down_payment_pct: number | null;
  years: number | null;
  frequency: Frequency | null;
  delivery_payment_pct: number | null;
  maintenance_pct: number | null;
  notes: string | null;
  // contracts-v2
  title: string | null;
  unit_type: string | null;
  bedrooms: number | null;
  image_urls: string[] | null;
  image_credit: string | null;
}

export interface ListingPage {
  items: Listing[];
  total: number;
  limit: number;
  offset: number;
}

export interface ListingQuery {
  area?: string;
  min_price?: number;
  max_price?: number;
  delivery_before?: string;
  bedrooms_min?: number;
  limit?: number;
  offset?: number;
}

export interface Payment {
  month: number;
  amount_egp: number;
  type: "down_payment" | "installment" | "delivery" | "maintenance";
}

export interface PlanResult {
  listing_id: string;
  plan_id: string;
  plan_type: "developer" | "mortgage";
  price_egp: number;
  down_payment_egp: number | null;
  down_payment_pct: number | null;
  delivery_payment_egp: number | null;
  delivery_month: number | null;
  installment_count: number | null;
  installment_egp: number | null;
  monthly_equivalent_egp: number | null;
  total_paid_egp: number | null;
  npv_egp: number | null;
  annual_discount_rate_pct: number | null;
  payments: Payment[] | null;
  missing_fields: string[];
  warnings: string[];
}

export interface AffordabilityResult {
  listing_id: string;
  plan_id: string;
  status: AffordabilityStatus;
  reason: string;
  down_payment_required_egp: number | null;
  down_payment_available_egp: number | null;
  down_payment_gap_egp: number | null;
  monthly_required_egp: number | null;
  monthly_capacity_egp: number | null;
  monthly_gap_egp: number | null;
  flags: string[];
  missing_fields: string[];
}

export interface UnitCard {
  listing: Listing;
  plan: PlanResult | null;
  affordability: AffordabilityResult | null;
}

export interface CompareResult {
  items: UnitCard[];
}

// ---------- Conversations ----------
export interface ChatMessage {
  message_id: string;
  role: MessageRole;
  text: string;
  created_at: string;
  cards: UnitCard[];
}

export interface ConversationView {
  conversation_id: string;
  mode: Mode;
  messages: ChatMessage[];
}

// ---------- Leads ----------
export interface MatchedUnit {
  listing_id: string;
  plan_id: string;
  affordability: AffordabilityStatus;
  liked?: boolean | null;
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
}

export interface LeadSummary {
  lead_id: string;
  conversation_id: string;
  score: number;
  band: Band;
  mode: Mode;
  main_interest: string | null;
  last_message_at: string;
}

export interface CountItem {
  key: string;
  count: number;
}

export interface AnalyticsResult {
  leads_by_band: Record<string, number>;
  top_areas: CountItem[];
  top_listings: CountItem[];
  p95_latency_ms: number | null;
  cache_hit_rate: number | null;
}

export interface ApiErrorBody {
  error: { code: string; message: string; request_id?: string };
}
