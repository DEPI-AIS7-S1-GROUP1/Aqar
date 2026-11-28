"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { logout, useSession } from "@/lib/auth";

const LINKS = [
  { href: "/home", label: "الرئيسية" },
  { href: "/chat", label: "المساعد" },
  { href: "/listings", label: "الوحدات" },
];

export default function CustomerHeader() {
  const session = useSession();
  const pathname = usePathname();
  const router = useRouter();
  const authed = session.status === "authed";
  const isBroker = authed && session.user.role === "broker";

  return (
    <header className="sticky top-0 z-30 bg-ink/95 backdrop-blur text-paper border-b border-paper/10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-xl font-[900] tracking-tight">
            AqarAI <span className="text-accent">.</span>
          </Link>
          <nav className="hidden sm:flex items-center gap-1 text-sm font-bold">
            {(isBroker ? [{ href: "/broker", label: "لوحة الوسيط" }, LINKS[2]] : authed ? LINKS : [LINKS[2]]).map((l) => {
              const active = pathname === l.href || (l.href !== "/home" && pathname.startsWith(l.href));
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  aria-current={active ? "page" : undefined}
                  className={`px-3 py-2 rounded-full transition-colors ${active ? "bg-paper/10 text-paper" : "text-muted-dark hover:text-paper"}`}
                >
                  {l.label}
                </Link>
              );
            })}
          </nav>
        </div>
        {authed ? (
          <div className="flex items-center gap-3">
            <span className="hidden md:inline text-xs text-muted-dark">{session.user.name}</span>
            <button
              type="button"
              onClick={() => {
                logout();
                router.replace("/");
              }}
              className="text-xs sm:text-sm font-bold px-3 py-2 rounded-full border border-paper/20 hover:bg-paper/10 transition-colors"
            >
              خروج
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm font-bold">
            <Link href="/login" className="px-3 py-2 rounded-full hover:bg-paper/10">دخول</Link>
            <Link href="/signup" className="px-4 py-2 rounded-full bg-accent">حساب جديد</Link>
          </div>
        )}
      </div>
      {authed && !isBroker && (
        <nav className="sm:hidden flex border-t border-paper/10 text-xs font-bold">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className={`flex-1 text-center py-2.5 ${pathname === l.href ? "text-paper" : "text-muted-dark"}`}>
              {l.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
