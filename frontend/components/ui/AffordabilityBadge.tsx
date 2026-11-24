import { AffordabilityStatus } from "@/lib/types";

interface AffordabilityBadgeProps {
  status: AffordabilityStatus;
  className?: string;
}

const BADGE_CONFIG: Record<
  AffordabilityStatus,
  { label: string; bg: string; text: string }
> = {
  fit: { label: "مناسبة", bg: "#DDF1E4", text: "#14532D" },
  tight: { label: "ضاغطة", bg: "#FCEBC8", text: "#7A4B00" },
  not_fit: { label: "مش مناسبة", bg: "#FBDADA", text: "#7F1D1D" },
  unknown: { label: "غير معروف", bg: "#E4E1D8", text: "#3F3F3A" },
};

export default function AffordabilityBadge({
  status,
  className = "",
}: AffordabilityBadgeProps) {
  const config = BADGE_CONFIG[status] || BADGE_CONFIG.unknown;

  return (
    <span
      style={{ backgroundColor: config.bg, color: config.text }}
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold select-none ${className}`}
    >
      {config.label}
    </span>
  );
}
