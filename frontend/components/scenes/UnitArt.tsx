// Generated illustration for a unit when it has no real photo yet (image_urls is null).
// Same listing id = same drawing. Labelled "رسم توضيحي" by the components that use it.
import { hashString, prng, windows } from "./prng";

export type ArtVariant = "day" | "dusk" | "interior" | "pool";

const PALETTES = [
  { wall: "#E8DCC6", shade: "#CDBE9F", accent: "#C8372F" },
  { wall: "#D9D4CB", shade: "#B9B1A3", accent: "#2F5D8C" },
  { wall: "#EADBC8", shade: "#C9AE8E", accent: "#B45309" },
  { wall: "#DCE3E1", shade: "#B6C2BF", accent: "#1C8AA6" },
];

export default function UnitArt({
  id,
  variant = "day",
  className = "",
}: {
  id: string;
  variant?: ArtVariant;
  className?: string;
}) {
  const seed = hashString(id);
  const r = prng(seed);
  const pal = PALETTES[seed % PALETTES.length];
  const gid = `ua-${seed}-${variant}`;

  if (variant === "interior") {
    return (
      <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" className={className} aria-hidden>
        <rect width="400" height="300" fill="#EFE7DA" />
        <rect y="210" width="400" height="90" fill="#C9AE8E" />
        <rect x="40" y="40" width="150" height="130" fill="#9ED0F0" stroke="#fff" strokeWidth="6" />
        <rect x="40" y="120" width="150" height="50" fill="#7FB0CC" />
        <polygon points="70,170 100,120 130,170" fill="#C68A55" opacity="0.7" />
        <line x1="115" y1="40" x2="115" y2="170" stroke="#fff" strokeWidth="4" />
        <rect x="220" y="160" width="150" height="50" rx="10" fill={pal.accent} opacity="0.85" />
        <rect x="214" y="140" width="162" height="34" rx="12" fill={pal.accent} />
        <rect x="236" y="150" width="40" height="24" rx="6" fill="#F4F1EA" opacity="0.8" />
        <rect x="120" y="230" width="160" height="10" rx="5" fill="#8D6E52" />
        <rect x="140" y="240" width="6" height="30" fill="#8D6E52" />
        <rect x="254" y="240" width="6" height="30" fill="#8D6E52" />
        <line x1="330" y1="40" x2="330" y2="90" stroke="#4A4A45" strokeWidth="2" />
        <path d="M312 110 L330 88 L348 110 Z" fill="#E9B872" />
        <circle cx="70" cy="250" r="16" fill="#5E8C5A" />
        <rect x="64" y="256" width="12" height="24" fill="#8D6E52" />
      </svg>
    );
  }

  if (variant === "pool") {
    return (
      <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" className={className} aria-hidden>
        <defs>
          <linearGradient id={`${gid}-s`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#8CCBE0" />
            <stop offset="1" stopColor="#EAF5F3" />
          </linearGradient>
        </defs>
        <rect width="400" height="300" fill={`url(#${gid}-s)`} />
        {[30, 130, 230, 310].map((x, i) => (
          <g key={x}>
            <rect x={x} y={90 - (i % 2) * 20} width="70" height={120 + (i % 2) * 20} fill={pal.wall} />
            <rect x={x} y={90 - (i % 2) * 20} width="70" height="8" fill={pal.shade} />
            {Array.from({ length: 4 }, (_, j) => (
              <rect key={j} x={x + 10} y={110 - (i % 2) * 20 + j * 26} width="50" height="12" fill="#5D7E8F" opacity="0.6" />
            ))}
          </g>
        ))}
        <rect y="200" width="400" height="100" fill="#E8DCC6" />
        <path d="M40 230 h320 v40 h-320 z" fill="#2FA3C2" />
        <path d="M60 244 q 20 -6 40 0 t 40 0 t 40 0 t 40 0 t 40 0 t 40 0" stroke="#BFE9F2" strokeWidth="2" fill="none" className="water-line" />
        {[20, 380].map((x) => (
          <g key={x} fill="#4F7A4A">
            <rect x={x - 2} y="150" width="4" height="70" fill="#6B5B4B" />
            <path d={`M${x} 150 q -24 -4 -34 10 q 18 -12 34 -6 z M${x} 150 q 24 -4 34 10 q -18 -12 -34 -6 z M${x} 150 q -6 -22 -2 -30 q 2 14 2 30 z`} />
          </g>
        ))}
      </svg>
    );
  }

  const dusk = variant === "dusk";
  const floors = 4 + Math.floor(r() * 5);
  const bw = 160 + Math.floor(r() * 80);
  const bx = 200 - bw / 2;
  const top = 250 - floors * 26;
  const wins = windows(seed, bx + 8, top + 10, bw - 16, floors * 26 - 14, Math.round(bw / 30), floors, dusk ? 0.6 : 0);

  return (
    <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" className={className} aria-hidden>
      <defs>
        <linearGradient id={`${gid}-s`} x1="0" y1="0" x2="0" y2="1">
          {dusk ? (
            <>
              <stop offset="0" stopColor="#1A1823" />
              <stop offset="0.7" stopColor="#7A3E37" />
              <stop offset="1" stopColor="#E19A5A" />
            </>
          ) : (
            <>
              <stop offset="0" stopColor="#9BCBE0" />
              <stop offset="1" stopColor="#F3EDE2" />
            </>
          )}
        </linearGradient>
      </defs>
      <rect width="400" height="300" fill={`url(#${gid}-s)`} />
      {dusk ? (
        <circle cx="330" cy="70" r="16" fill="#F4F1EA" opacity="0.85" />
      ) : (
        <circle cx="70" cy="60" r="22" fill="#FFF1C9" />
      )}
      <rect x={bx - 40} y={top + 40} width="40" height={250 - top - 40} fill={dusk ? "#2A2530" : pal.shade} />
      <rect x={bx + bw} y={top + 60} width="46" height={250 - top - 60} fill={dusk ? "#2A2530" : pal.shade} />
      <rect x={bx} y={top} width={bw} height={250 - top} fill={dusk ? "#3A3340" : pal.wall} />
      <rect x={bx - 6} y={top - 8} width={bw + 12} height="10" fill={dusk ? "#2A2530" : pal.shade} />
      {Array.from({ length: floors }, (_, f) => (
        <rect key={f} x={bx - 4} y={top + 24 + f * 26} width={bw + 8} height="3" fill={dusk ? "#2A2530" : pal.shade} />
      ))}
      {wins.map((w, i) => (
        <rect
          key={i}
          x={w.x}
          y={w.y}
          width={w.w}
          height={w.h}
          rx="1.5"
          fill={dusk ? (w.lit ? "#F2C27E" : "#1F1B25") : "#6E93A6"}
          opacity={dusk ? 1 : 0.75}
        />
      ))}
      <rect x={196 - 12} y="226" width="32" height="24" fill={pal.accent} />
      <rect y="250" width="400" height="50" fill={dusk ? "#1A1820" : "#D7C8A8"} />
      {[40, 360].map((x) => (
        <g key={x} fill={dusk ? "#0E1116" : "#4F7A4A"}>
          <rect x={x - 2} y="196" width="4" height="56" fill={dusk ? "#0E1116" : "#6B5B4B"} />
          <path d={`M${x} 196 q -22 -4 -30 9 q 16 -11 30 -5 z M${x} 196 q 22 -4 30 9 q -16 -11 -30 -5 z M${x} 196 q -5 -20 -2 -27 q 2 13 2 27 z`} />
        </g>
      ))}
    </svg>
  );
}
