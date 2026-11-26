"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import BrokerHeader from "@/components/broker/BrokerHeader";
import MessageBubble from "@/components/chat/MessageBubble";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import BandBadge from "@/components/ui/BandBadge";
import ModeBadge from "@/components/ui/ModeBadge";
import { UnitPhoto } from "@/components/units/UnitCard";
import { api, ApiError } from "@/lib/api";
import {
  areaLabel,
  formatEgp,
  formatValue,
  PURPOSE_LABEL,
  TIMELINE_LABEL,
  TRIGGER_LABEL,
  UNKNOWN,
} from "@/lib/format";
import type { ConversationView, LeadBrief, Listing, Mode } from "@/lib/types";

const POLL_MS = 3000;

const SLOT_LABEL: Record<string, string> = {
  areas: "المنطقة",
  down_payment_available_egp: "المقدم المتاح",
  monthly_capacity_egp: "القسط الشهري",
  timeline: "التوقيت",
  purpose: "الغرض",
  bedrooms_min: "عدد الغرف",
};

function Section({ title, children, aside }: { title: string; children: React.ReactNode; aside?: React.ReactNode }) {
  return (
    <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-line/30">
        <h2 className="text-base sm:text-lg font-[900] text-ink">{title}</h2>
        {aside}
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export default function LeadDetailClient() {
  const { id } = useParams<{ id: string }>();
  const [brief, setBrief] = useState<LeadBrief | null>(null);
  const [conv, setConv] = useState<ConversationView | null>(null);
  const [units, setUnits] = useState<Record<string, Listing>>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const refresh = useCallback(async () => {
    const [b, leads] = await Promise.all([api.brokerLead(id), api.brokerLeads()]);
    setBrief(b);
    const convId = leads.find((l) => l.lead_id === id)?.conversation_id;
    if (convId) setConv(await api.conversation(convId));
    return b;
  }, [id]);

  useEffect(() => {
    let alive = true;
    const tick = () =>
      refresh().catch((e) => alive && setError(e instanceof ApiError ? e.message : "مش قادرين نجيب بيانات العميل."));
    tick();
    const t = setInterval(() => !document.hidden && tick(), POLL_MS);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [refresh]);

  // fetch unit details for the suggested units (once each)
  const unitIds = brief?.matched_units.map((u) => u.listing_id).join(",") ?? "";
  useEffect(() => {
    let alive = true;
    unitIds
      .split(",")
      .filter(Boolean)
      .forEach((uid) =>
        api
          .listing(uid)
          .then((l) => alive && setUnits((m) => (m[uid] ? m : { ...m, [uid]: l })))
          .catch(() => null)
      );
    return () => {
      alive = false;
    };
  }, [unitIds]);

  const msgCount = conv?.messages.length ?? 0;
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [msgCount]);

  const mode: Mode = conv?.mode ?? "AI_ACTIVE";

  async function act(name: "takeover" | "release" | "close") {
    setBusy(name);
    setActionError(null);
    try {
      if (name === "takeover") await api.takeover(id);
      else if (name === "release") await api.release(id);
      else await api.close(id);
      await refresh();
    } catch (e) {
      setActionError(e instanceof ApiError ? e.message : "العملية ماتمتش.");
    } finally {
      setBusy(null);
    }
  }

  async function sendBroker(e: FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text) return;
    setBusy("send");
    setActionError(null);
    try {
      await api.brokerMessage(id, text);
      setDraft("");
      await refresh();
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : "الرسالة ماتبعتتش.");
    } finally {
      setBusy(null);
    }
  }

  if (error && !brief) {
    return (
      <div className="min-h-[100svh] bg-sand">
        <BrokerHeader />
        <main className="max-w-md mx-auto px-4 py-24 text-center">
          <div className="bg-white border border-line/40 rounded-2xl p-8">
            <h1 className="text-xl font-[900] text-ink">{error}</h1>
            <Link href="/broker" className="mt-6 inline-block bg-ink text-paper px-6 py-2.5 rounded-full text-sm font-bold">
              الرجوع لقائمة العملاء
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const c = brief?.confirmed;

  return (
    <div className="min-h-[100svh] bg-sand flex flex-col">
      <BrokerHeader />
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-8 py-8 flex flex-col gap-6">
        <Link href="/broker" className="text-sm font-bold text-muted hover:text-ink self-start">← كل العملاء</Link>

        {!brief ? (
          <div className="skeleton h-28 rounded-2xl" />
        ) : (
          <div className="msg-in bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-[900] text-ink tracking-tight">عميل {brief.lead_id}</h1>
              <BandBadge band={brief.band} score={brief.score} />
              <ModeBadge mode={mode} />
            </div>

            {/* Takeover controls */}
            <div className="flex flex-wrap items-center gap-2">
              {(mode === "AI_ACTIVE" || mode === "HANDOFF_PENDING") && (
                <button
                  type="button"
                  onClick={() => act("takeover")}
                  disabled={busy !== null}
                  className={`rounded-full bg-accent text-paper px-5 py-2.5 text-sm font-bold shadow-lg shadow-accent/25 hover:-translate-y-[2px] transition-transform disabled:opacity-60 ${
                    mode === "HANDOFF_PENDING" ? "pulse-ring" : ""
                  }`}
                >
                  {busy === "takeover" ? "بنستلم…" : "استلم المحادثة"}
                </button>
              )}
              {mode === "HUMAN_ACTIVE" && (
                <button type="button" onClick={() => act("release")} disabled={busy !== null} className="rounded-full border border-ink px-5 py-2.5 text-sm font-bold hover:bg-ink hover:text-paper transition-colors disabled:opacity-60">
                  رجّعه للمساعد
                </button>
              )}
              {mode !== "CLOSED" && (
                <button type="button" onClick={() => act("close")} disabled={busy !== null} className="rounded-full px-4 py-2.5 text-sm font-bold text-muted hover:text-ink disabled:opacity-60">
                  اقفل العميل
                </button>
              )}
            </div>
          </div>
        )}
        {actionError && <p role="alert" className="rounded-2xl bg-[#FBDADA] text-[#7F1D1D] px-4 py-3 text-sm">{actionError}</p>}

        {brief && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 flex flex-col gap-6">
              <Section title="الملخص">
                <p className="text-xs text-muted">
                  <span className="font-bold text-ink">سبب التحويل: </span>
                  {TRIGGER_LABEL[brief.trigger] ?? (brief.trigger === "in_progress" ? "لسه بيتأهل مع المساعد" : formatValue(brief.trigger))}
                </p>
                <p className="mt-3 text-sm sm:text-base text-ink leading-relaxed bg-sand/40 p-4 rounded-xl border border-line/20">
                  {formatValue(brief.summary_text)}
                </p>
              </Section>

              {/* Live conversation */}
              <Section
                title="المحادثة"
                aside={<span className="text-xs text-muted">{mode === "HUMAN_ACTIVE" ? "أنت مستلم دلوقتي" : "المساعد هو اللي بيرد"}</span>}
              >
                <div className="max-h-[460px] overflow-y-auto flex flex-col gap-3 bg-sand/50 rounded-xl p-3">
                  {conv ? conv.messages.map((m) => <MessageBubble key={m.message_id} message={m} />) : <div className="skeleton h-24 rounded-xl" />}
                  <div ref={endRef} />
                </div>
                <form onSubmit={sendBroker} className="mt-3 flex items-end gap-2">
                  <label htmlFor="broker-msg" className="sr-only">رسالة للعميل</label>
                  <textarea
                    id="broker-msg"
                    dir="auto"
                    rows={1}
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    disabled={mode !== "HUMAN_ACTIVE" || busy !== null}
                    placeholder={mode === "HUMAN_ACTIVE" ? "اكتب للعميل…" : "استلم المحادثة الأول عشان تكتب"}
                    className="flex-1 min-h-[46px] max-h-32 resize-none rounded-3xl border border-line px-4 py-3 text-sm disabled:bg-sand"
                  />
                  <button type="submit" disabled={mode !== "HUMAN_ACTIVE" || !draft.trim() || busy !== null} className="min-h-[46px] px-5 rounded-full bg-ink text-paper text-sm font-bold disabled:opacity-40">
                    ابعت
                  </button>
                </form>
              </Section>

              <Section title={`الوحدات اللي اتعرضت (${brief.matched_units.length.toLocaleString("ar-EG")})`}>
                {brief.matched_units.length ? (
                  <div className="grid sm:grid-cols-2 gap-3">
                    {brief.matched_units.map((u) => {
                      const l = units[u.listing_id];
                      return (
                        <Link key={u.listing_id} href={`/listings/${u.listing_id}`} className="rounded-xl border border-line/40 overflow-hidden hover:shadow-md transition-shadow">
                          {l ? <UnitPhoto listing={l} className="h-24" variant="dusk" /> : <div className="skeleton h-24" />}
                          <div className="p-3">
                            <div className="flex items-start justify-between gap-2">
                              <span className="font-bold text-sm">{l?.title ?? u.listing_id}</span>
                              <AffordabilityBadge status={u.affordability} />
                            </div>
                            <p className="mt-1 text-xs text-muted">{l ? `${formatEgp(l.price_egp)} · ${areaLabel(l.area)}` : "…"}</p>
                            <p className="mt-1 text-[11px] text-muted">
                              رأي العميل: {u.liked === true ? "عجبته" : u.liked === false ? "ماعجبتوش" : UNKNOWN}
                            </p>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-muted bg-sand/30 p-4 rounded-xl text-center">لسه مفيش وحدات اتعرضت.</p>
                )}
              </Section>
            </div>

            <div className="lg:col-span-5 flex flex-col gap-6 lg:sticky lg:top-24">
              <Section title="المتطلبات المؤكدة">
                <dl className="flex flex-col gap-3 text-sm">
                  {(
                    [
                      ["المنطقة", c?.areas ? c.areas.map(areaLabel).join("، ") : UNKNOWN],
                      ["المقدم المتاح", formatEgp(c?.down_payment_available_egp)],
                      ["القسط الشهري", formatEgp(c?.monthly_capacity_egp)],
                      ["التوقيت", c?.timeline ? TIMELINE_LABEL[c.timeline] : UNKNOWN],
                      ["الغرض", c?.purpose ? PURPOSE_LABEL[c.purpose] : UNKNOWN],
                    ] as [string, string][]
                  ).map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between gap-3 pb-2 border-b border-line/20 last:border-0">
                      <dt className="text-muted">{k}</dt>
                      <dd className={`font-bold ${v === UNKNOWN ? "text-muted font-normal" : "text-ink"}`}>{v}</dd>
                    </div>
                  ))}
                </dl>
              </Section>

              <Section title="لسه مش متأكد">
                {brief.unconfirmed.length ? (
                  <div className="flex flex-wrap gap-2">
                    {brief.unconfirmed.map((s) => (
                      <span key={s} className="bg-sand text-muted px-3 py-1 rounded-full text-xs font-medium border border-line/30">
                        {SLOT_LABEL[s] ?? s}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted">كل البيانات الأساسية متأكدة.</p>
                )}
              </Section>

              <Section title="ليه التقييم ده؟">
                {brief.reasons.length ? (
                  <ul className="flex flex-col gap-2 text-sm">
                    {brief.reasons.map((r) => (
                      <li key={r} className="flex items-start gap-2">
                        <span className="mt-2 w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                        {r}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-muted">{UNKNOWN}</p>
                )}
              </Section>

              <Section title="أسئلة مفتوحة">
                {brief.open_questions.length ? (
                  <ul className="flex flex-col gap-2 text-sm list-disc pr-5">
                    {brief.open_questions.map((q) => <li key={q}>{q}</li>)}
                  </ul>
                ) : (
                  <p className="text-xs text-muted">مفيش أسئلة مفتوحة.</p>
                )}
              </Section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
