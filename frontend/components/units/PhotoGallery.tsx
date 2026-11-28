"use client";

import Image from "next/image";
import { useRef, useState, type KeyboardEvent, type PointerEvent } from "react";
import UnitArt, { type ArtVariant } from "@/components/scenes/UnitArt";
import type { Listing } from "@/lib/types";

type Slide = { kind: "photo"; src: string } | { kind: "art"; variant: ArtVariant; label: string };

const ART: Slide[] = [
  { kind: "art", variant: "day", label: "الواجهة" },
  { kind: "art", variant: "dusk", label: "بالليل" },
  { kind: "art", variant: "interior", label: "من جوه" },
  { kind: "art", variant: "pool", label: "الكمبوند" },
];

export default function PhotoGallery({ listing }: { listing: Listing }) {
  const slides: Slide[] = listing.image_urls?.length
    ? listing.image_urls.map((src) => ({ kind: "photo", src }))
    : ART;
  const [i, setI] = useState(0);
  const startX = useRef<number | null>(null);
  const n = slides.length;
  const go = (d: number) => setI((v) => (v + d + n) % n);

  const onKey = (e: KeyboardEvent) => {
    // RTL: the arrow pointing to the start (right) goes back
    if (e.key === "ArrowLeft") go(1);
    if (e.key === "ArrowRight") go(-1);
  };
  const onDown = (e: PointerEvent) => (startX.current = e.clientX);
  const onUp = (e: PointerEvent) => {
    if (startX.current === null) return;
    const dx = e.clientX - startX.current;
    startX.current = null;
    if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
  };

  const alt = `${listing.title ?? "وحدة"}، صورة`;

  return (
    <div>
      <div
        role="region"
        aria-roledescription="معرض صور"
        aria-label={`صور ${listing.title ?? "الوحدة"}`}
        tabIndex={0}
        onKeyDown={onKey}
        onPointerDown={onDown}
        onPointerUp={onUp}
        className="relative aspect-[4/3] sm:aspect-[16/10] rounded-[28px] overflow-hidden bg-sand touch-pan-y select-none focus:outline-none focus-visible:ring-4 focus-visible:ring-accent/40"
      >
        {slides.map((s, k) => (
          <div
            key={k}
            aria-hidden={k !== i}
            className="absolute inset-0 transition-all duration-700 ease-out"
            style={{ opacity: k === i ? 1 : 0, transform: k === i ? "scale(1)" : "scale(1.06)" }}
          >
            {s.kind === "photo" ? (
              <Image src={s.src} alt={`${alt} ${k + 1}`} fill sizes="(max-width: 1024px) 100vw, 700px" className="object-cover" priority={k === 0} />
            ) : (
              <UnitArt id={listing.listing_id} variant={s.variant} className="w-full h-full" />
            )}
          </div>
        ))}
        <div className="absolute inset-x-0 bottom-0 p-4 flex items-end justify-between bg-gradient-to-t from-ink/60 to-transparent text-paper">
          <span className="text-xs">
            {(i + 1).toLocaleString("ar-EG")} / {n.toLocaleString("ar-EG")}
            {slides[i].kind === "art" ? ` · رسم توضيحي: ${(slides[i] as { label: string }).label}` : ""}
          </span>
          <div className="flex gap-2">
            <button type="button" onClick={() => go(-1)} aria-label="الصورة اللي فاتت" className="w-10 h-10 rounded-full bg-paper/90 text-ink flex items-center justify-center hover:bg-paper">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden><path d="M9 6l6 6-6 6" /></svg>
            </button>
            <button type="button" onClick={() => go(1)} aria-label="الصورة اللي بعدها" className="w-10 h-10 rounded-full bg-paper/90 text-ink flex items-center justify-center hover:bg-paper">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden><path d="M15 6l-6 6 6 6" /></svg>
            </button>
          </div>
        </div>
      </div>
      <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
        {slides.map((s, k) => (
          <button
            key={k}
            type="button"
            onClick={() => setI(k)}
            aria-label={`صورة ${k + 1}`}
            aria-current={k === i}
            className={`relative shrink-0 w-24 h-16 rounded-xl overflow-hidden border-2 transition-all ${k === i ? "border-accent" : "border-transparent opacity-60 hover:opacity-100"}`}
          >
            {s.kind === "photo" ? (
              <Image src={s.src} alt="" fill sizes="96px" className="object-cover" />
            ) : (
              <UnitArt id={listing.listing_id} variant={s.variant} className="w-full h-full" />
            )}
          </button>
        ))}
      </div>
      {listing.image_credit && <p className="mt-2 text-[11px] text-muted">مصدر الصور: {listing.image_credit}</p>}
    </div>
  );
}
