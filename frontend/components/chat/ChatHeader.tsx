"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth";
import type { Mode } from "@/lib/types";

const STATUS: Record<Mode, { text: string; dot: string }> = {
  AI_ACTIVE: { text: "متاح دلوقتي", dot: "bg-emerald-500" },
  HANDOFF_PENDING: { text: "بنوصلك بمستشار…", dot: "bg-warm" },
  HUMAN_ACTIVE: { text: "مستشار من الفريق معاك", dot: "bg-accent" },
  CLOSED: { text: "المحادثة مقفولة", dot: "bg-muted-dark" },
};

export default function ChatHeader({ mode = "AI_ACTIVE" }: { mode?: Mode }) {
  const router = useRouter();
  const s = STATUS[mode];
  return (
    <header className="sticky top-0 z-20 w-full bg-ink text-paper px-4 py-3 sm:px-6 border-b border-paper/10">
      <div className="max-w-3xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link href="/home" aria-label="الرجوع للرئيسية" className="w-10 h-10 rounded-full hover:bg-paper/10 flex items-center justify-center">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden><path d="M9 6l6 6-6 6" /></svg>
          </Link>
          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-[900] ${mode === "HUMAN_ACTIVE" ? "bg-paper text-ink" : "bg-accent text-paper"}`} aria-hidden>
            {mode === "HUMAN_ACTIVE" ? "م" : "ع"}
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold leading-tight">{mode === "HUMAN_ACTIVE" ? "مستشار عقار" : "مساعد عقار"}</h1>
            <p className="flex items-center gap-1.5 text-xs text-muted-dark mt-0.5" aria-live="polite">
              <span className={`w-2 h-2 rounded-full inline-block ${s.dot} ${mode === "HANDOFF_PENDING" ? "pulse-ring" : ""}`} />
              {s.text}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs sm:text-sm font-bold">
          <Link href="/listings" className="px-3 py-2 rounded-full text-muted-dark hover:text-paper hover:bg-paper/10">الوحدات</Link>
          <button
            type="button"
            onClick={() => {
              logout();
              router.replace("/");
            }}
            className="px-3 py-2 rounded-full text-muted-dark hover:text-paper hover:bg-paper/10"
          >
            خروج
          </button>
        </div>
      </div>
    </header>
  );
}
