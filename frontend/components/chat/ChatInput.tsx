"use client";

import { useState, FormEvent, KeyboardEvent } from "react";

export interface ChatInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
}

export default function ChatInput({
  onSendMessage,
  disabled = false,
}: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e?: FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSendMessage(trimmed);
    setText("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="sticky bottom-0 z-20 w-full bg-paper border-t border-line/40 px-4 py-3 sm:px-6 sm:py-3.5 shadow-md">
      <form
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto flex items-center gap-2.5 sm:gap-3"
      >
        <label htmlFor="chat-message-input" className="sr-only">
          اكتب رسالتك
        </label>
        <input
          id="chat-message-input"
          type="text"
          dir="auto"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="اكتب استفسارك هنا (مثلاً: شقة في New Cairo)..."
          className="flex-1 min-h-[44px] bg-white border border-line/60 rounded-full px-5 py-2.5 text-sm sm:text-base text-ink placeholder:text-muted focus:outline-none focus:border-ink transition-colors duration-200"
        />

        <button
          type="submit"
          disabled={!text.trim() || disabled}
          aria-label="إرسال"
          className="w-11 h-11 min-w-[44px] min-h-[44px] rounded-full bg-ink text-paper flex items-center justify-center transition-colors duration-200 hover:bg-accent disabled:opacity-40 disabled:hover:bg-ink cursor-pointer disabled:cursor-not-allowed shadow-sm"
        >
          <svg
            className="w-5 h-5 rtl:rotate-180"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
}
