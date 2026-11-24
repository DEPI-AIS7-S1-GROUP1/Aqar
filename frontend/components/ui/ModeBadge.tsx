import { Mode } from "@/lib/types";

interface ModeBadgeProps {
  mode: Mode;
  className?: string;
}

const MODE_LABELS: Record<Mode, string> = {
  AI_ACTIVE: "الـ AI شغال",
  HANDOFF_PENDING: "في انتظار الموظف",
  HUMAN_ACTIVE: "الموظف مستلم",
  CLOSED: "مقفولة",
};

export default function ModeBadge({ mode, className = "" }: ModeBadgeProps) {
  const label = MODE_LABELS[mode] || mode;

  return (
    <span
      style={{ backgroundColor: "#3F3F3A", color: "#E4E1D8" }}
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border border-line/30 select-none ${className}`}
    >
      {label}
    </span>
  );
}
