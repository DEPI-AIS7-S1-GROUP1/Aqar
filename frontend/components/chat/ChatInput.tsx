"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";

export interface ChatInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  /** text to start with (e.g. a question about a unit). Change `key` on the component to reset. */
  initialText?: string;
  suggestions?: string[];
  placeholder?: string;
}

export default function ChatInput({
  onSendMessage,
  disabled = false,
  initialText = "",
  suggestions = [],
  placeholder = "اكتب رسالتك… (مثلاً: شقة في التجمع بمقدم مليون)",
}: ChatInputProps) {
  const [text, setText] = useState(initialText);

  const send = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSendMessage(trimmed);
    setText("");
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    send(text);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      send(text);
    }
  };

  return (
    <div className="sticky bottom-0 z-20 w-full bg-paper/95 backdrop-blur border-t border-line/50 px-4 pt-2.5 pb-3 sm:px-6">
      {suggestions.length > 0 && !disabled && (
        <div className="max-w-3xl mx-auto flex gap-2 overflow-x-auto pb-2.5 -mx-1 px-1" aria-label="ردود مقترحة">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => send(s)}
              className="shrink-0 rounded-full border border-line bg-white px-3.5 py-2 text-xs font-bold text-ink hover:border-ink hover:-translate-y-[1px] transition-all"
            >
              {s}
            </button>
          ))}
        </div>
      )}
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex items-end gap-2.5">
        <label htmlFor="chat-message-input" className="sr-only">
          اكتب رسالتك
        </label>
        <textarea
          id="chat-message-input"
          dir="auto"
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className="flex-1 min-h-[46px] max-h-32 resize-none bg-white border border-line/70 rounded-3xl px-5 py-3 text-sm sm:text-base text-ink placeholder:text-muted focus:outline-none focus:border-ink transition-colors disabled:bg-sand"
        />
        <button
          type="submit"
          disabled={!text.trim() || disabled}
          aria-label="إرسال"
          className="w-[46px] h-[46px] shrink-0 rounded-full bg-ink text-paper flex items-center justify-center transition-all hover:bg-accent hover:scale-105 disabled:opacity-40 disabled:hover:bg-ink disabled:hover:scale-100 cursor-pointer disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5 rtl:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
}
