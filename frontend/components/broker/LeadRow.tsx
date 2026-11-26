import Link from "next/link";
import BandBadge from "@/components/ui/BandBadge";
import ModeBadge from "@/components/ui/ModeBadge";
import { formatValue, relativeTime } from "@/lib/format";
import type { LeadSummary } from "@/lib/types";

const BAR_COLORS: Record<string, string> = {
  hot: "bg-hot",
  warm: "bg-warm",
  cold: "bg-cold",
};

export default function LeadRow({ lead, now, fresh = false }: { lead: LeadSummary; now: number; fresh?: boolean }) {
  const ready = lead.band === "hot" && lead.mode === "AI_ACTIVE";
  const waiting = lead.mode === "HANDOFF_PENDING";
  return (
    <Link
      href={`/broker/leads/${lead.lead_id}`}
      className={`msg-in block w-full bg-white border rounded-[14px] p-4 sm:p-5 shadow-sm transition-all duration-200 hover:-translate-y-[2px] hover:shadow-md ${
        waiting ? "border-warm/60 ring-2 ring-warm/20" : fresh ? "border-accent/50" : "border-line/40 hover:border-line"
      }`}
    >
      <div className="grid grid-cols-1 sm:grid-cols-[auto_1fr_auto] sm:items-center gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-sand/60 flex flex-col items-center justify-center shrink-0">
            <span className="text-lg font-[900] text-ink leading-none">{lead.score.toLocaleString("ar-EG")}</span>
            <span className="text-[10px] text-muted font-bold mt-0.5">نقطة</span>
          </div>
          <div className="flex flex-col gap-1.5 min-w-[170px]">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-bold text-sm sm:text-base text-ink">عميل {lead.lead_id}</span>
              <BandBadge band={lead.band} />
              {ready && <span className="rounded-full bg-accent/10 text-accent text-[11px] font-bold px-2 py-0.5">جاهز</span>}
            </div>
            <div className="w-full bg-sand h-2 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${BAR_COLORS[lead.band]} transition-all duration-700`} style={{ width: `${Math.min(100, Math.max(0, lead.score))}%` }} />
            </div>
          </div>
        </div>
        <div className="text-xs sm:text-sm text-ink leading-relaxed sm:px-4">
          <span className="text-muted block text-[11px] mb-0.5">الاهتمام الرئيسي:</span>
          <span className="font-medium">{formatValue(lead.main_interest)}</span>
        </div>
        <div className="flex sm:flex-col items-center sm:items-end justify-between gap-2 text-xs text-muted">
          <ModeBadge mode={lead.mode} />
          <span>{relativeTime(lead.last_message_at, now)}</span>
        </div>
      </div>
    </Link>
  );
}
