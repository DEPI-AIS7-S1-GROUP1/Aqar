// All data goes through here. Mock mode (NEXT_PUBLIC_USE_MOCKS=true, or no API URL set)
// runs the in-browser demo backend in lib/mock/ with the exact same paths and shapes.
import type {
  AnalyticsResult,
  AuthResponse,
  Band,
  ChatMessage,
  CompareResult,
  ConversationView,
  LeadBrief,
  LeadSummary,
  Listing,
  ListingPage,
  ListingQuery,
  LoginRequest,
  PlanResult,
  SignupRequest,
  User,
} from "./types";
import { getToken } from "./auth";

export const USE_MOCKS =
  process.env.NEXT_PUBLIC_USE_MOCKS === "true" || !process.env.NEXT_PUBLIC_API_URL;

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

async function request<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> {
  const token = getToken();
  if (USE_MOCKS) {
    const { mockRequest, MockHttpError } = await import("./mock/router");
    try {
      return await mockRequest<T>(method, path, body, token);
    } catch (e) {
      if (e instanceof MockHttpError) throw new ApiError(e.status, e.code, e.message);
      throw new ApiError(500, "internal", "حصلت مشكلة. جرّب تاني.");
    }
  }

  const base = process.env.NEXT_PUBLIC_API_URL ?? "";
  let res: Response;
  try {
    res = await fetch(`${base}/api/v1${path}`, {
      method,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "network", "مفيش اتصال بالسيرفر. اتأكد من النت وجرّب تاني.");
  }
  if (res.status === 204) return null as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = (data as { error?: { code?: string; message?: string } } | null)?.error;
    throw new ApiError(
      res.status,
      err?.code ?? "error",
      err?.message ??
        (res.status === 429 ? "في ضغط دلوقتي. استنى لحظة وجرّب تاني." : "حصلت مشكلة. جرّب تاني.")
    );
  }
  return data as T;
}

function qs(params: Record<string, string | number | undefined | null>): string {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export const api = {
  signup: (b: SignupRequest) => request<AuthResponse>("POST", "/auth/signup", b),
  login: (b: LoginRequest) => request<AuthResponse>("POST", "/auth/login", b),
  me: () => request<User>("GET", "/auth/me"),

  areas: () => request<string[]>("GET", "/areas"),
  listings: (q: ListingQuery) =>
    request<ListingPage>("GET", `/listings${qs({ ...q })}`),
  listing: (id: string) => request<Listing>("GET", `/listings/${encodeURIComponent(id)}`),
  plans: (id: string, rate?: number | null) =>
    request<PlanResult[]>(
      "GET",
      `/listings/${encodeURIComponent(id)}/plans${qs({ annual_discount_rate_pct: rate ?? undefined })}`
    ),
  compare: (ids: string[], rate: number) =>
    request<CompareResult>("POST", "/compare", { listing_ids: ids, annual_discount_rate_pct: rate }),
  viewListing: (id: string) =>
    request<null>("POST", "/events/listing-view", { listing_id: id }).catch(() => null),

  myConversation: () => request<ConversationView>("GET", "/conversations/mine"),
  startConversation: () => request<ConversationView>("POST", "/conversations"),
  send: (id: string, text: string) =>
    request<ConversationView>("POST", `/conversations/${id}/messages`, { text }),
  conversation: (id: string, after?: string | null) =>
    request<ConversationView>("GET", `/conversations/${id}${qs({ after: after ?? undefined })}`),

  brokerLeads: (band?: Band) => request<LeadSummary[]>("GET", `/broker/leads${qs({ band })}`),
  brokerLead: (id: string) => request<LeadBrief>("GET", `/broker/leads/${id}`),
  takeover: (id: string) => request<ConversationView>("POST", `/broker/leads/${id}/takeover`),
  brokerMessage: (id: string, text: string) =>
    request<ChatMessage>("POST", `/broker/leads/${id}/messages`, { text }),
  release: (id: string) => request<ConversationView>("POST", `/broker/leads/${id}/release`),
  close: (id: string) => request<LeadSummary>("POST", `/broker/leads/${id}/close`),
  analytics: () => request<AnalyticsResult>("GET", "/broker/analytics"),
};

/** @deprecated kept for old imports; use `api` instead. */
export async function apiGet<T>(path: string): Promise<T | null> {
  try {
    return await request<T>("GET", path);
  } catch {
    return null;
  }
}
