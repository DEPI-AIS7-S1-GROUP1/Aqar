"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { homeFor, useSession } from "@/lib/auth";

export default function SiteNav() {
  const session = useSession();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const authed = session.status === "authed";
  const dest = authed ? homeFor(session.user.role, session.isNew) : "/signup";

  return (
    <header
      className={`fixed top-0 inset-x-0 z-40 transition-all duration-500 ${
        scrolled ? "bg-ink/80 backdrop-blur-md border-b border-paper/10 py-3" : "py-6"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 flex items-center justify-between gap-4 text-paper">
        <Link href="/" className="text-2xl font-[900] tracking-tight hover:-translate-y-[2px] transition-transform">
          AqarAI <span className="text-accent">.</span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-sm font-bold text-muted-dark">
          <a href="#services" className="hover:text-paper transition-colors">خدماتنا</a>
          <a href="#how" className="hover:text-paper transition-colors">إزاي بيشتغل</a>
          <a href="#cities" className="hover:text-paper transition-colors">المناطق</a>
          <Link href="/listings" className="hover:text-paper transition-colors">الوحدات</Link>
        </div>

        <div className="hidden md:flex items-center gap-3">
          {authed ? (
            <Link
              href={dest}
              className="bg-paper text-ink text-sm font-bold px-5 py-2.5 rounded-full hover:bg-accent hover:text-paper hover:-translate-y-[2px] transition-all"
            >
              {session.user.role === "broker" ? "لوحة الوسيط" : "حسابي"}
            </Link>
          ) : (
            <>
              <Link href="/login" className="text-sm font-bold px-4 py-2.5 rounded-full hover:bg-paper/10 transition-colors">
                تسجيل الدخول
              </Link>
              <Link
                href="/signup"
                className="bg-accent text-paper text-sm font-bold px-5 py-2.5 rounded-full shadow-lg shadow-accent/25 hover:-translate-y-[2px] transition-transform"
              >
                إنشاء حساب
              </Link>
            </>
          )}
        </div>

        <button
          type="button"
          className="md:hidden w-11 h-11 rounded-full border border-paper/20 flex items-center justify-center"
          aria-label={open ? "قفل القائمة" : "فتح القائمة"}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </nav>

      {open && (
        <div className="md:hidden mx-4 mt-3 rounded-2xl bg-ink/95 backdrop-blur border border-paper/10 p-4 flex flex-col gap-1 text-paper text-sm font-bold">
          {[
            ["#services", "خدماتنا"],
            ["#how", "إزاي بيشتغل"],
            ["#cities", "المناطق"],
          ].map(([href, label]) => (
            <a key={href} href={href} onClick={() => setOpen(false)} className="px-3 py-3 rounded-xl hover:bg-paper/10">
              {label}
            </a>
          ))}
          <Link href="/listings" className="px-3 py-3 rounded-xl hover:bg-paper/10">الوحدات</Link>
          {authed ? (
            <Link href={dest} className="mt-2 text-center bg-paper text-ink px-4 py-3 rounded-full">حسابي</Link>
          ) : (
            <div className="mt-2 grid grid-cols-2 gap-2">
              <Link href="/login" className="text-center border border-paper/20 px-4 py-3 rounded-full">دخول</Link>
              <Link href="/signup" className="text-center bg-accent px-4 py-3 rounded-full">حساب جديد</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
