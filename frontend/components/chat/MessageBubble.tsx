import Link from "next/link";
import UnitCard from "@/components/units/UnitCard";
import { formatTime } from "@/lib/format";
import type { ChatMessage } from "@/lib/types";

export interface MessageBubbleProps {
  message: ChatMessage;
  pending?: boolean;
  failed?: boolean;
  onRetry?: () => void;
}

export default function MessageBubble({ message, pending = false, failed = false, onRetry }: MessageBubbleProps) {
  const { role, text, cards, created_at } = message;
  const sources = message.sources ?? [];

  if (role === "system") {
    return (
      <div className="msg-in self-center my-1 rounded-full bg-ink/5 border border-line/60 px-4 py-1.5 text-xs text-muted" role="note">
        {text}
      </div>
    );
  }

  const isUser = role === "user";
  const isBroker = role === "broker";

  return (
    <div className={`msg-in flex flex-col max-w-[88%] sm:max-w-[80%] ${isUser ? "self-start items-start" : "self-end items-end"}`}>
      {isBroker && (
        <span className="mb-1 inline-flex items-center gap-1.5 text-[11px] font-bold text-accent">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" />
          مستشار من الفريق
        </span>
      )}
      <div
        dir="auto"
        className={`rounded-2xl px-4 py-3 text-sm sm:text-[15px] leading-relaxed break-words shadow-sm ${
          isUser
            ? `bg-white text-ink border ${failed ? "border-accent" : "border-line/40"} ${pending ? "opacity-70" : ""}`
            : isBroker
            ? "bg-[#FBEDEC] text-ink border border-accent/30"
            : "bg-ink text-paper"
        }`}
      >
        <p className="whitespace-pre-line">{text}</p>

        {cards.length > 0 && (
          <div className="mt-3 grid gap-2.5 sm:grid-cols-2" dir="rtl">
            {cards.map((c) => (
              <UnitCard key={c.listing.listing_id} listing={c.listing} plan={c.plan} affordability={c.affordability} compact />
            ))}
          </div>
        )}
        {sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5" dir="rtl" aria-label="مصادر الإجابة">
            {sources.map((src) => (
              <a
                key={src.url}
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                title={src.url}
                className="inline-flex max-w-full items-center gap-1.5 rounded-full border border-paper/25 bg-paper/10 px-3 py-1 text-[11px] text-paper/85 hover:bg-paper hover:text-ink transition-colors"
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" className="h-3 w-3 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5" />
                  <path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5" />
                </svg>
                <span className="truncate">المصدر: {src.title}</span>
              </a>
            ))}
          </div>
        )}
        {cards.length >= 2 && (
          <Link
            href={`/compare?ids=${cards.slice(0, 3).map((c) => c.listing.listing_id).join(",")}`}
            className="mt-3 inline-flex items-center gap-2 rounded-full bg-paper text-ink px-4 py-2 text-xs font-bold hover:bg-accent hover:text-paper transition-colors"
          >
            قارن الوحدات دي
          </Link>
        )}
      </div>
      <span className="text-[10px] sm:text-[11px] mt-1 px-1.5 text-muted">
        {failed ? (
          <button type="button" onClick={onRetry} className="text-accent font-bold underline">
            ماتبعتتش. ابعت تاني
          </button>
        ) : pending ? (
          "بيتبعت..."
        ) : (
          formatTime(created_at)
        )}
      </span>
    </div>
  );
}
