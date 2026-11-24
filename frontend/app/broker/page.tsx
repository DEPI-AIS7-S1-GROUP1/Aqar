"use client";

import { useEffect, useState, useMemo } from "react";
import BrokerHeader from "@/components/broker/BrokerHeader";
import LeadRow from "@/components/broker/LeadRow";
import { apiGet } from "@/lib/api";
import { LeadSummary, Band } from "@/lib/types";
import { SAMPLE_LEADS } from "@/lib/sample-data";

type FilterType = "all" | Band;

export default function BrokerLeadsPage() {
  const [leads, setLeads] = useState<LeadSummary[]>(SAMPLE_LEADS);
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");

  useEffect(() => {
    async function loadLeads() {
      try {
        const data = await apiGet<LeadSummary[] | { leads: LeadSummary[] }>(
          "/broker/leads",
          "leads"
        );
        if (data) {
          const loaded = Array.isArray(data) ? data : data.leads;
          if (loaded && loaded.length > 0) {
            setLeads(loaded);
          }
        }
      } catch {
        // Fallback to SAMPLE_LEADS
      }
    }
    loadLeads();
  }, []);

  // Filter chips with exact counts
  const counts = useMemo(() => {
    return {
      all: leads.length,
      hot: leads.filter((l) => l.band === "hot").length,
      warm: leads.filter((l) => l.band === "warm").length,
      cold: leads.filter((l) => l.band === "cold").length,
    };
  }, [leads]);

  // Sorted by score descending, filtered client-side
  const filteredLeads = useMemo(() => {
    const list =
      activeFilter === "all"
        ? leads
        : leads.filter((l) => l.band === activeFilter);
    return [...list].sort((a, b) => b.score - a.score);
  }, [leads, activeFilter]);

  return (
    <div className="min-h-screen bg-sand flex flex-col">
      {/* Top bar on ink */}
      <BrokerHeader />

      {/* Main leads content */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-8 py-8 flex flex-col gap-6">
        {/* Title + subtitle */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-line/40 pb-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-[900] text-ink tracking-tight">
              العملاء
            </h1>
            <p className="text-sm text-muted mt-1">
              مرتبين من الأعلى تقييمًا وفق الجدية والملاءة المالية
            </p>
          </div>
        </div>

        {/* Filter chips with real counts */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => setActiveFilter("all")}
            className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-200 cursor-pointer ${
              activeFilter === "all"
                ? "bg-ink text-paper shadow-sm"
                : "bg-white text-muted hover:text-ink border border-line/40 hover:border-line"
            }`}
          >
            الكل ({counts.all})
          </button>

          <button
            onClick={() => setActiveFilter("hot")}
            className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-200 cursor-pointer flex items-center gap-1.5 ${
              activeFilter === "hot"
                ? "bg-hot text-white shadow-sm"
                : "bg-white text-muted hover:text-hot border border-line/40 hover:border-hot/40"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-hot" />
            Hot ({counts.hot})
          </button>

          <button
            onClick={() => setActiveFilter("warm")}
            className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-200 cursor-pointer flex items-center gap-1.5 ${
              activeFilter === "warm"
                ? "bg-warm text-white shadow-sm"
                : "bg-white text-muted hover:text-warm border border-line/40 hover:border-warm/40"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-warm" />
            Warm ({counts.warm})
          </button>

          <button
            onClick={() => setActiveFilter("cold")}
            className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition-all duration-200 cursor-pointer flex items-center gap-1.5 ${
              activeFilter === "cold"
                ? "bg-cold text-white shadow-sm"
                : "bg-white text-muted hover:text-cold border border-line/40 hover:border-cold/40"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-cold" />
            Cold ({counts.cold})
          </button>
        </div>

        {/* Leads rows list */}
        {filteredLeads.length > 0 ? (
          <div className="flex flex-col gap-3.5">
            {filteredLeads.map((lead) => (
              <LeadRow key={lead.lead_id} lead={lead} />
            ))}
          </div>
        ) : (
          <div className="bg-white border border-line/40 rounded-2xl p-10 text-center text-muted">
            <p className="text-base font-bold text-ink">
              لا يوجد عملاء في هذه الفئة حالياً
            </p>
            <p className="text-xs text-muted mt-1">
              جرّب اختيار تصنيف آخر من القائمة أعلاه
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
