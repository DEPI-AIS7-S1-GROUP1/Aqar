export interface MessageBubbleProps {
  role: "customer" | "user" | "assistant";
  content: string;
  timestamp?: string;
  hasUnitCards?: boolean;
}

export default function MessageBubble({
  role,
  content,
  timestamp,
  hasUnitCards = false,
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

        {/* Placeholder slot for UnitCard when message has unit cards */}
        {hasUnitCards && (
          <div
            className="mt-3 border-2 border-dashed border-line/60 rounded-xl p-4 text-center text-xs font-bold text-muted-dark bg-paper/5 select-none"
            aria-label="خانة بطاقة الوحدة - سيتم إضافتها من العضو 2"
          >
            UnitCard — Member 2
          </div>
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
