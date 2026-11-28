"use client";

import Link from "next/link";
import { useRef, type CSSProperties, type ReactNode } from "react";
import { useParallax } from "@/components/motion/hooks";

export default function AuthShell({
  scene,
  title,
  subtitle,
  caption,
  children,
}: {
  scene: ReactNode;
  title: string;
  subtitle: string;
  caption: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useParallax(ref);
  return (
    <div ref={ref} className="min-h-[100svh] bg-ink text-paper grid lg:grid-cols-2">
      {/* form side (right in RTL) */}
      <div className="relative flex flex-col px-5 sm:px-10 lg:px-16 py-8">
        <Link href="/" className="text-2xl font-[900] tracking-tight self-start hover:-translate-y-[2px] transition-transform">
          AqarAI <span className="text-accent">.</span>
        </Link>
        <div className="flex-1 flex items-center">
          <div className="w-full max-w-md mx-auto py-10">
            <h1 className="rise-line text-3xl sm:text-4xl font-[900] tracking-tight">
              <span>{title}</span>
            </h1>
            <p className="fade-in mt-3 text-muted-dark leading-relaxed" style={{ animationDelay: "0.2s" }}>
              {subtitle}
            </p>
            <div className="fade-in mt-8" style={{ animationDelay: "0.35s" }}>
              {children}
            </div>
          </div>
        </div>
      </div>

      {/* scene side */}
      <div className="relative hidden lg:block overflow-hidden m-3 rounded-[32px]">
        <div className="plx absolute inset-[-3%]" style={{ "--d": 18 } as CSSProperties}>
          {scene}
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-ink/80 via-transparent to-transparent" />
        <p className="absolute bottom-8 right-8 left-8 text-2xl font-[900] leading-snug max-w-sm">{caption}</p>
      </div>
    </div>
  );
}

export function Field({
  label,
  id,
  hint,
  error,
  ...input
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string; id: string; hint?: string; error?: string }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-bold text-paper/90 mb-2">
        {label}
      </label>
      <input
        id={id}
        {...input}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${id}-err` : hint ? `${id}-hint` : undefined}
        className={`w-full min-h-[48px] rounded-2xl bg-paper/[0.06] border px-4 text-paper placeholder:text-muted-dark/60 focus:outline-none focus:bg-paper/[0.09] transition-colors ${
          error ? "border-accent" : "border-paper/15 focus:border-paper/50"
        }`}
      />
      {error ? (
        <p id={`${id}-err`} className="mt-1.5 text-xs text-[#F3A29C]">
          {error}
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="mt-1.5 text-xs text-muted-dark">
          {hint}
        </p>
      ) : null}
    </div>
  );
}

export function SubmitButton({ busy, children }: { busy: boolean; children: ReactNode }) {
  return (
    <button
      type="submit"
      disabled={busy}
      className="w-full min-h-[52px] rounded-full bg-accent text-paper font-bold shadow-xl shadow-accent/25 hover:-translate-y-[2px] transition-transform disabled:opacity-60 disabled:translate-y-0 inline-flex items-center justify-center gap-2"
    >
      {busy && <span className="w-4 h-4 rounded-full border-2 border-paper/40 border-t-paper animate-spin" aria-hidden />}
      {children}
    </button>
  );
}
