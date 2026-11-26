import Image from "next/image";
import Link from "next/link";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import UnitArt from "@/components/scenes/UnitArt";
import { areaLabel, formatDate, formatEgp, formatValue } from "@/lib/format";
import type { AffordabilityResult, Listing, PlanResult } from "@/lib/types";

export function UnitPhoto({ listing, className = "", variant = "day" }: { listing: Listing; className?: string; variant?: "day" | "dusk" }) {
  const src = listing.image_urls?.[0];
  return (
    <div className={`relative overflow-hidden bg-sand ${className}`}>
      {src ? (
        <Image
          src={src}
          alt={`${listing.title ?? "وحدة"} في ${areaLabel(listing.area)}`}
          fill
          sizes="(max-width: 640px) 100vw, 400px"
          className="object-cover"
        />
      ) : (
        <>
          <UnitArt id={listing.listing_id} variant={variant} className="absolute inset-0 w-full h-full" />
          <span className="absolute bottom-2 left-2 rounded-full bg-ink/60 text-paper text-[10px] px-2 py-0.5 backdrop-blur">رسم توضيحي</span>
        </>
      )}
    </div>
  );
}

export default function UnitCard({
  listing,
  plan = null,
  affordability = null,
  compact = false,
  selected,
  onToggleSelect,
}: {
  listing: Listing;
  plan?: PlanResult | null;
  affordability?: AffordabilityResult | null;
  compact?: boolean;
  selected?: boolean;
  onToggleSelect?: () => void;
}) {
  return (
    <article
      className={`group relative bg-white text-ink rounded-[20px] overflow-hidden border transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-ink/10 ${
        selected ? "border-accent ring-2 ring-accent/40" : "border-line/50"
      }`}
    >
      <Link href={`/listings/${listing.listing_id}`} className="block focus:outline-none focus-visible:ring-4 focus-visible:ring-accent/40">
        <UnitPhoto listing={listing} className={compact ? "h-28" : "h-48"} variant={compact ? "dusk" : "day"} />
        <div className={compact ? "p-3" : "p-4"}>
          <div className="flex items-start justify-between gap-2">
            <h3 className={`font-bold leading-snug ${compact ? "text-[13px]" : "text-base"}`}>{listing.title ?? `وحدة ${listing.listing_id}`}</h3>
            {affordability && <AffordabilityBadge status={affordability.status} className="shrink-0" />}
          </div>
          <p className={`mt-1 font-[900] ${compact ? "text-sm" : "text-lg"}`}>{formatEgp(listing.price_egp)}</p>
          <p className="mt-1 text-xs text-muted">
            {areaLabel(listing.area)} · {formatValue(listing.area_sqm)} م² · {listing.bedrooms === null ? "غرف غير متوفر" : `${listing.bedrooms.toLocaleString("ar-EG")} غرف`}
          </p>
          {!compact && (
            <p className="mt-1 text-xs text-muted">
              {listing.developer} · استلام {formatDate(listing.delivery_date)}
            </p>
          )}
          {plan && (
            <p className={`mt-2 text-xs leading-relaxed ${compact ? "text-muted" : "bg-sand/60 rounded-xl px-3 py-2"}`}>
              مقدم {formatEgp(plan.down_payment_egp)} · قسط شهري {formatEgp(plan.monthly_equivalent_egp)}
            </p>
          )}
          {affordability && !compact && <p className="mt-2 text-xs text-muted leading-relaxed">{affordability.reason}</p>}
        </div>
      </Link>
      {onToggleSelect && (
        <button
          type="button"
          onClick={onToggleSelect}
          aria-pressed={selected}
          className={`absolute top-3 right-3 rounded-full px-3 py-1.5 text-xs font-bold backdrop-blur transition-colors ${
            selected ? "bg-accent text-paper" : "bg-ink/60 text-paper hover:bg-ink/80"
          }`}
        >
          {selected ? "مختارة للمقارنة" : "+ قارن"}
        </button>
      )}
    </article>
  );
}
