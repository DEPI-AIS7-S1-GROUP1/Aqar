import { ChatMessage } from "@/lib/types";
import InlineUnitCard from "@/components/chat/InlineUnitCard";

export interface MessageBubbleProps {
  role: "customer" | "user" | "assistant";
  content: string;
  timestamp?: string;
  unit?: ChatMessage["unit"];
}

export default function MessageBubble({
  role,
  content,
  timestamp,
  unit,
}: MessageBubbleProps) {
  const isCustomer = role === "customer" || role === "user";

  return (
    <div
      className={`flex flex-col ${
        isCustomer ? "self-start items-start" : "self-end items-end"
      } max-w-[80%]`}
    >
      <div
        dir="auto"
        className={`rounded-2xl p-4 text-sm sm:text-base leading-relaxed break-words shadow-sm ${
          isCustomer
            ? "bg-white text-ink border border-line/30"
            : "bg-ink text-paper"
        }`}
      >
        <p className="whitespace-pre-line">{content}</p>

        {/* Unit card slot when message has a recommended unit */}
        {unit && (
          <InlineUnitCard
            priceEgp={unit.price_egp}
            planSummary={unit.plan_summary}
            affordability={unit.affordability}
            title={unit.title}
          />
        )}
      </div>

      {timestamp && (
        <span
          className={`text-[10px] sm:text-[11px] mt-1 px-1.5 ${
            isCustomer ? "text-muted" : "text-muted-dark"
          }`}
        >
          {timestamp}
        </span>
      )}
    </div>
  );
}
