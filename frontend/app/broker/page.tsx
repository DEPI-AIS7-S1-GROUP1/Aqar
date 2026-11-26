"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import RequireRole from "@/components/auth/RequireRole";
import BrokerHeader from "@/components/broker/BrokerHeader";
import LeadRow from "@/components/broker/LeadRow";
import { api, ApiError } from "@/lib/api";
import type { Band, LeadSummary } from "@/lib/types";

type FilterType = "all" | Band;
const POLL_MS = 3000;

const CHIPS: { key: FilterType; label: string; on: string; dot?: string }[] = [
  { key: "all", label: "الكل", on: "bg-ink text-paper" },
  { key: "hot", label: "Hot", on: "bg-hot text-white", dot: "bg-hot" },
  { key: "warm", label: "Warm", on: "bg-warm text-white", dot: "bg-warm" },
  { key: "cold", label: "Cold", on: "bg-cold text-white", dot: "bg-cold" },
];

function LeadsInner() {
  const [leads, setLeads] = useState<LeadSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>("all");
  const [now, setNow] = useState(0);
  const [fresh, setFresh] = useState<Set<string>>(new Set());
  const known = useRef<Set<string> | null>(null);

  useEffect(() => {
    let alive = true;
    const load = () =>
      api
        .brokerLeads()
        .then((list) => {
          if (!alive) return;
          const ids = new Set(list.map((l) => l.lead_id));
          if (known.current) {
            const added = list.filter((l) => !known.current!.has(l.lead_id)).map((l) => l.lead_id);
            if (added.length) setFresh(new Set(added));
          }
          known.current = ids;
          setLeads(list);
          setNow(Date.now());
          setError(null);
        })
        .catch((e) => alive && setError(e instanceof ApiError ? e.message : "مش قادرين نجيب العملاء."));
    load();
    const t = setInterval(() => !document.hidden && load(), POLL_MS);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const counts = useMemo(() => {
    const l = leads ?? [];
    return {
      all: l.length,
      hot: l.filter((x) => x.band === "hot").length,
      warm: l.filter((x) => x.band === "warm").length,
      cold: l.filter((x) => x.band === "cold").length,
    };
  }, [leads]);

  const shown = useMemo(() => {
    const l = leads ?? [];
    return [...(filter === "all" ? l : l.filter((x) => x.band === filter))].sort((a, b) => b.score - a.score);
  }, [leads, filter]);

  const waiting = (leads ?? []).filter((l) => l.mode === "HANDOFF_PENDING").length;

  return (
    <div className="min-h-[100svh] bg-sand flex flex-col">
      <BrokerHeader />
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-8 py-8 flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 border-b border-line/40 pb-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-[900] text-ink tracking-tight">العملاء</h1>
            <p className="text-sm text-muted mt-1">مرتبين من الأعلى تقييمًا. بتتحدث لوحدها كل كام ثانية.</p>
          </div>
          {waiting > 0 && (
            <div className="msg-in flex items-center gap-2 rounded-full bg-[#FCEBC8] text-[#7A4B00] px-4 py-2 text-sm font-bold" role="status">
              <span className="w-2 h-2 rounded-full bg-warm pulse-ring" />
              {waiting.toLocaleString("ar-EG")} عميل مستني وسيط
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2.5" role="group" aria-label="فلترة حسب التقييم">
          {CHIPS.map((c) => (
            <button
              key={c.key}
              type="button"
              aria-pressed={filter === c.key}
              onClick={() => setFilter(c.key)}
              className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all flex items-center gap-1.5 ${
                filter === c.key ? `${c.on} shadow-sm` : "bg-white text-muted hover:text-ink border border-line/40"
              }`}
            >
              {c.dot && <span className={`w-2 h-2 rounded-full ${c.dot}`} />}
              {c.label} ({counts[c.key].toLocaleString("ar-EG")})
            </button>
          ))}
        </div>

        {error && <p role="alert" className="rounded-2xl bg-[#FBDADA] text-[#7F1D1D] px-4 py-3 text-sm">{error}</p>}

        {leads === null && !error ? (
          <div className="flex flex-col gap-3.5">
            {Array.from({ length: 4 }, (_, i) => <div key={i} className="skeleton h-24 rounded-[14px]" />)}
          </div>
        ) : shown.length > 0 ? (
          <div className="flex flex-col gap-3.5">
            {shown.map((lead) => (
              <LeadRow key={lead.lead_id} lead={lead} now={now} fresh={fresh.has(lead.lead_id)} />
            ))}
          </div>
        ) : (
          <div className="bg-white border border-line/40 rounded-2xl p-10 text-center">
            <p className="text-base font-bold text-ink">مفيش عملاء في الفئة دي دلوقتي</p>
            <p className="text-xs text-muted mt-1">جرّب تصنيف تاني من فوق.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default function BrokerLeadsPage() {
  return (
    <RequireRole role="broker">
      <LeadsInner />
    </RequireRole>
  );
}
