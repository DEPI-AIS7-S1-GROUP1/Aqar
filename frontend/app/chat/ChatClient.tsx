"use client";

import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import ChatHeader from "@/components/chat/ChatHeader";
import ChatInput from "@/components/chat/ChatInput";
import MessageBubble from "@/components/chat/MessageBubble";
import TypingDots from "@/components/chat/TypingDots";
import { api, ApiError } from "@/lib/api";
import { markNotNew } from "@/lib/auth";
import type { ChatMessage, ConversationView, Mode } from "@/lib/types";

interface Pending {
  tempId: string;
  text: string;
  failed: boolean;
}

const POLL_MS = 3000;

function mergeMessages(prev: ChatMessage[], incoming: ChatMessage[]): ChatMessage[] {
  const seen = new Set(prev.map((m) => m.message_id));
  const add = incoming.filter((m) => !seen.has(m.message_id));
  return add.length ? [...prev, ...add] : prev;
}

/** Quick replies that match what the assistant just asked. */
function suggestionsFor(last: ChatMessage | undefined, mode: Mode): string[] {
  if (mode !== "AI_ACTIVE" || !last || last.role !== "ai") return [];
  const t = last.text;
  if (/أنهي منطقة|منطقة؟/.test(t)) return ["عايز شقة في التجمع", "بدور في الشيخ زايد", "العاصمة الإدارية", "شاليه في الساحل"];
  if (/مقدم قد إيه/.test(t)) return ["معايا مقدم مليون", "مقدم 500 ألف", "مقدم 2 مليون"];
  if (/القسط/.test(t) && /كام/.test(t)) return ["القسط ميزيدش عن 40 ألف", "قسط 25 ألف في الشهر", "قسط 70 ألف"];
  if (/إمتى/.test(t)) return ["عايز أشتري الشهر ده", "خلال سنة", "مش مستعجل"];
  if (/للسكن ولا للاستثمار/.test(t)) return ["للسكن", "للاستثمار"];
  return ["قارن بين الوحدات", "أقدر أعاين السبت؟", "عايز أكلم حد من الفريق"];
}

export default function ChatClient() {
  const sp = useSearchParams();
  const ask = sp.get("ask");
  const [conv, setConv] = useState<ConversationView | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [pending, setPending] = useState<Pending[]>([]);
  const [typing, setTyping] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const convRef = useRef<ConversationView | null>(null);

  useEffect(() => {
    convRef.current = conv;
  }, [conv]);

  // load or start the conversation
  useEffect(() => {
    let alive = true;
    api
      .myConversation()
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) return api.startConversation();
        throw e;
      })
      .then((c) => {
        if (!alive) return;
        setConv(c);
        markNotNew();
      })
      .catch((e) => alive && setLoadError(e instanceof ApiError ? e.message : "مش قادرين نفتح المحادثة دلوقتي."));
    return () => {
      alive = false;
    };
  }, []);

  // poll for broker / AI messages
  const convId = conv?.conversation_id;
  useEffect(() => {
    if (!convId) return;
    const t = setInterval(() => {
      if (document.hidden) return;
      const c = convRef.current;
      const last = c?.messages[c.messages.length - 1]?.message_id ?? null;
      api
        .conversation(convId, last)
        .then((v) =>
          setConv((prev) =>
            prev ? { ...prev, mode: v.mode, messages: mergeMessages(prev.messages, v.messages) } : prev
          )
        )
        .catch(() => null);
    }, POLL_MS);
    return () => clearInterval(t);
  }, [convId]);

  // keep the newest message in view
  const count = (conv?.messages.length ?? 0) + pending.length + (typing ? 1 : 0);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [count]);

  const send = useCallback(
    async (text: string, retryId?: string) => {
      const c = convRef.current;
      if (!c) return;
      const tempId = retryId ?? `tmp-${Math.random().toString(36).slice(2)}`;
      setSendError(null);
      setPending((p) => (retryId ? p.map((x) => (x.tempId === retryId ? { ...x, failed: false } : x)) : [...p, { tempId, text, failed: false }]));
      setTyping(c.mode === "AI_ACTIVE");
      try {
        const v = await api.send(c.conversation_id, text);
        setConv((prev) => (prev ? { ...prev, mode: v.mode, messages: mergeMessages(prev.messages, v.messages) } : prev));
        setPending((p) => p.filter((x) => x.tempId !== tempId));
      } catch (e) {
        setPending((p) => p.map((x) => (x.tempId === tempId ? { ...x, failed: true } : x)));
        setSendError(e instanceof ApiError ? e.message : "الرسالة ماتبعتتش.");
      } finally {
        setTyping(false);
      }
    },
    []
  );

  const mode: Mode = conv?.mode ?? "AI_ACTIVE";
  const messages = conv?.messages ?? [];
  const last = messages[messages.length - 1];
  const closed = mode === "CLOSED";

  return (
    <div className="min-h-[100svh] bg-sand flex flex-col">
      <ChatHeader mode={mode} />

      {mode === "HANDOFF_PENDING" && (
        <div className="msg-in bg-[#FCEBC8] text-[#7A4B00] text-sm px-4 py-2.5 text-center border-b border-warm/20" role="status">
          مستشار من الفريق هيدخل المحادثة خلال دقايق. ملخص طلبك وصله.
        </div>
      )}
      {mode === "HUMAN_ACTIVE" && (
        <div className="msg-in bg-ink text-paper text-sm px-4 py-2.5 text-center" role="status">
          أنت دلوقتي بتكلم مستشار من الفريق.
        </div>
      )}

      <main className="flex-1 w-full max-w-3xl mx-auto px-4 py-6 sm:px-6 flex flex-col gap-4" aria-live="polite" aria-busy={typing}>
        {!conv && !loadError && (
          <div className="flex flex-col gap-3">
            <div className="skeleton h-16 w-2/3 self-end rounded-2xl" />
            <div className="skeleton h-10 w-1/2 rounded-2xl" />
          </div>
        )}
        {loadError && (
          <div role="alert" className="rounded-2xl bg-white border border-line/50 p-6 text-center">
            <p className="font-bold text-ink">{loadError}</p>
            <button type="button" onClick={() => window.location.reload()} className="mt-4 bg-ink text-paper px-5 py-2.5 rounded-full text-sm font-bold">
              جرّب تاني
            </button>
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.message_id} message={m} />
        ))}
        {pending.map((p) => (
          <MessageBubble
            key={p.tempId}
            message={{ message_id: p.tempId, role: "user", text: p.text, created_at: "", cards: [] }}
            pending={!p.failed}
            failed={p.failed}
            onRetry={() => send(p.text, p.tempId)}
          />
        ))}
        {typing && <TypingDots />}
        {sendError && <p className="self-center text-xs text-accent" role="alert">{sendError}</p>}
        <div ref={endRef} className="h-4 shrink-0" />
      </main>

      <ChatInput
        key={ask ?? "chat"}
        onSendMessage={(t) => send(t)}
        disabled={!conv || closed || typing}
        initialText={ask ? `عايز أعرف أكتر عن الوحدة ${ask}، وهل تناسب المقدم والقسط بتوعي؟` : ""}
        suggestions={suggestionsFor(last, mode)}
        placeholder={closed ? "المحادثة مقفولة" : mode === "HUMAN_ACTIVE" ? "اكتب للمستشار…" : undefined}
      />
    </div>
  );
}
