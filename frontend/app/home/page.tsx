"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";
import RequireRole from "@/components/auth/RequireRole";
import CustomerHeader from "@/components/ui/CustomerHeader";
import Reveal from "@/components/motion/Reveal";
import { MiniCairo } from "@/components/scenes/CairoScene";
import { MiniCoast, MiniPyramids } from "@/components/scenes/MiniScenes";
import { api } from "@/lib/api";
import { useSession } from "@/lib/auth";
import type { ConversationView } from "@/lib/types";

/** Builds the "saved search" link from what the customer already told the assistant. */
function savedSearchHref(conv: ConversationView | null): string | null {
  if (!conv) return null;
  // the latest AI message with cards tells us which area was searched
  const withCards = [...conv.messages].reverse().find((m) => m.cards.length > 0);
  const area = withCards?.cards[0]?.listing.area;
  return area ? `/listings?area=${area}` : null;
}

function OptionCard({
  href,
  scene,
  kicker,
  title,
  body,
  delay,
}: {
  href: string;
  scene: ReactNode;
  kicker: string;
  title: string;
  body: string;
  delay: number;
}) {
  return (
    <Reveal delay={delay} variant="scale" className="h-full">
      <Link
        href={href}
        className="group relative flex flex-col justify-end h-full min-h-[320px] rounded-[28px] overflow-hidden text-paper shadow-xl shadow-ink/10 focus:outline-none focus-visible:ring-4 focus-visible:ring-accent/50"
      >
        <div className="absolute inset-0 transition-transform duration-[1.2s] group-hover:scale-105">{scene}</div>
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/40 to-transparent" />
        <div className="relative p-6">
          <p className="text-xs font-bold text-gold">{kicker}</p>
          <h2 className="mt-1 text-2xl font-[900]">{title}</h2>
          <p className="mt-2 text-sm text-paper/80 leading-relaxed">{body}</p>
          <span className="mt-4 inline-flex w-11 h-11 rounded-full bg-paper text-ink items-center justify-center transition-transform group-hover:-translate-x-1">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden>
              <path d="M19 12H5M11 18l-6-6 6-6" />
            </svg>
          </span>
        </div>
      </Link>
    </Reveal>
  );
}

function HomeInner() {
  const session = useSession();
  const [conv, setConv] = useState<ConversationView | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let alive = true;
    api
      .myConversation()
      .then((c) => alive && setConv(c))
      .catch(() => null)
      .finally(() => alive && setLoaded(true));
    return () => {
      alive = false;
    };
  }, []);

  const name = session.status === "authed" ? session.user.name : "";
  const saved = savedSearchHref(conv);

  return (
    <div className="min-h-[100svh] bg-paper">
      <CustomerHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
        <Reveal>
          <p className="text-accent font-bold text-sm">أهلاً {name}</p>
          <h1 className="mt-2 text-4xl sm:text-5xl font-[900] tracking-tight text-ink">نكمل منين النهارده؟</h1>
        </Reveal>

        <div className="mt-10 grid md:grid-cols-3 gap-5">
          <OptionCard
            href="/chat"
            delay={0}
            scene={<MiniCairo />}
            kicker="المساعد"
            title={conv ? "كمّل مع المساعد" : "ابدأ مع المساعد"}
            body={conv ? "المحادثة محفوظة. كمّل من آخر حتة وقفت عندها." : "احكيله بتدور على إيه، وهو يرشحلك اللي تقدر عليه."}
          />
          <OptionCard
            href="/listings"
            delay={120}
            scene={<MiniPyramids />}
            kicker="تصفح"
            title="استكشف الوحدات"
            body="كل الوحدات بفلتر المنطقة والسعر والاستلام، ومعاها الصور وخطط السداد."
          />
          <OptionCard
            href={saved ?? "/chat"}
            delay={240}
            scene={<MiniCoast />}
            kicker="البحث المحفوظ"
            title="بحثي المحفوظ"
            body={
              saved
                ? "الوحدات في المنطقة اللي قلتها للمساعد، جاهزة بالفلتر."
                : loaded
                ? "لسه مفيش بحث محفوظ. قول للمساعد المنطقة والمقدم والقسط وهيتحفظ."
                : "بنحمّل بحثك..."
            }
          />
        </div>
      </main>
    </div>
  );
}

export default function CustomerHomePage() {
  return (
    <RequireRole role="customer">
      <HomeInner />
    </RequireRole>
  );
}
