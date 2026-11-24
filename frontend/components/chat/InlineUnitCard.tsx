// TEMPORARY until Member 2's UnitCard merges
import { AffordabilityStatus } from "@/lib/types";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";

export interface InlineUnitCardProps {
  priceEgp: number;
  planSummary: string;
  affordability: AffordabilityStatus;
  title?: string;
}

export default function InlineUnitCard({
  priceEgp,
  planSummary,
  affordability,
  title = "شقة سكنية مميزة في New Cairo",
}: InlineUnitCardProps) {
  return (
    <div className="mt-3 bg-white text-ink border border-line/50 rounded-xl p-4 shadow-sm select-none">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-bold text-sm sm:text-base text-ink">{title}</h3>
        <AffordabilityBadge status={affordability} />
      </div>

      <div className="mt-2 text-base sm:text-lg font-[900] text-ink">
        {priceEgp.toLocaleString("ar-EG")} جنيه
      </div>

      <p className="mt-1 text-xs sm:text-sm text-muted leading-relaxed">
        {planSummary}
      </p>

      <div className="mt-3 pt-2.5 border-t border-line/30 flex items-center justify-between text-[11px] text-muted">
        <span>خطة سداد مرنة</span>
        <span className="text-[10px] bg-sand px-2 py-0.5 rounded text-muted font-medium">
          أرقام توضيحية
        </span>
      </div>
    </div>
  );
}
