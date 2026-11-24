import Link from "next/link";
import { LeadSummary } from "@/lib/types";
import BandBadge from "@/components/ui/BandBadge";

export interface LeadRowProps {
  lead: LeadSummary;
}

const BAR_COLORS: Record<string, string> = {
  hot: "bg-[#C8372F]",
  warm: "bg-[#B45309]",
  cold: "bg-[#2F5D8C]",
};

export default function LeadRow({ lead }: LeadRowProps) {
  const barColor = BAR_COLORS[lead.band] || "bg-[#2F5D8C]";

  return (
    <Link
      href={`/broker/leads/${lead.lead_id}`}
      className="block w-full bg-white border border-line/40 rounded-[14px] p-4 sm:p-5 shadow-sm transition-all duration-200 hover:-translate-y-[2px] hover:shadow-md hover:border-line"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Left/Start side: Lead ID, Score, Progress bar, Band Badge */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-sand/60 flex flex-col items-center justify-center shrink-0">
            <span className="text-lg font-[900] text-ink leading-none">
              {lead.score}
            </span>
            <span className="text-[10px] text-muted font-bold mt-0.5">نقطة</span>
          </div>

          <div className="flex flex-col gap-1.5 min-w-[140px]">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm sm:text-base text-ink">
                عميل {lead.lead_id}
              </span>
              <BandBadge band={lead.band} />
            </div>

            {/* Progress bar in band color */}
            <div className="w-full bg-sand h-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${barColor} transition-all duration-300`}
                style={{ width: `${Math.min(100, Math.max(0, lead.score))}%` }}
              />
            </div>
          </div>
        </div>

        {/* Middle: Main interest line */}
        <div className="flex-1 sm:px-4 text-xs sm:text-sm text-ink leading-relaxed">
          <span className="text-muted block text-[11px] mb-0.5">
            الاهتمام الرئيسي:
          </span>
          <span className="font-medium">{lead.main_interest}</span>
        </div>

        {/* End side: Time since last message */}
        <div className="text-left shrink-0 text-xs text-muted">
          <span>{lead.time_since_last_message}</span>
        </div>
      </div>
    </Link>
  );
}
