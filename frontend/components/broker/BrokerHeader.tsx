"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { logout, useSession } from "@/lib/auth";

const TABS = [
  { href: "/broker", label: "العملاء" },
  { href: "/broker/analytics", label: "التحليلات" },
];

export default function BrokerHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const session = useSession();
  return (
    <header className="sticky top-0 z-30 w-full bg-ink text-paper px-4 sm:px-8 border-b border-paper/10">
      <div className="max-w-6xl mx-auto h-16 flex items-center justify-between gap-4">
        <div className="flex items-center gap-6 sm:gap-10">
          <Link href="/broker" className="text-xl sm:text-2xl font-[900] tracking-tight">
            AqarAI <span className="text-accent">.</span>
          </Link>
          <nav className="flex items-center gap-5 text-sm font-bold h-16">
            {TABS.map((t) => {
              const active = t.href === "/broker" ? pathname === "/broker" || pathname.startsWith("/broker/leads") : pathname.startsWith(t.href);
              return (
                <Link
                  key={t.href}
                  href={t.href}
                  aria-current={active ? "page" : undefined}
                  className={`relative h-full flex items-center transition-colors ${active ? "text-paper" : "text-muted-dark hover:text-paper"}`}
                >
                  {t.label}
                  <span className={`absolute bottom-0 inset-x-0 h-[3px] rounded-full bg-accent transition-transform duration-300 ${active ? "scale-x-100" : "scale-x-0"}`} />
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-3 text-xs sm:text-sm">
          {session.status === "authed" && <span className="hidden md:inline text-muted-dark">{session.user.name}</span>}
          <button
            type="button"
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="font-bold px-3 py-2 rounded-full border border-paper/20 hover:bg-paper/10"
          >
            خروج
          </button>
        </div>
      </div>
    </header>
  );
}
