import { Band } from "@/lib/types";

interface BandBadgeProps {
  band: Band;
  score?: number;
  className?: string;
}

const BAND_CONFIG: Record<
  Band,
  { label: string; bg: string; text: string }
> = {
  hot: { label: "Hot", bg: "#C8372F", text: "#FFFFFF" },
  warm: { label: "Warm", bg: "#B45309", text: "#FFFFFF" },
  cold: { label: "Cold", bg: "#2F5D8C", text: "#FFFFFF" },
};

export default function BandBadge({
  band,
  score,
  className = "",
}: BandBadgeProps) {
  const config = BAND_CONFIG[band] || BAND_CONFIG.cold;

  return (
    <span
      style={{ backgroundColor: config.bg, color: config.text }}
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold select-none ${className}`}
    >
      <span>{config.label}</span>
      {score !== undefined && <span>· {score}</span>}
    </span>
  );
}
