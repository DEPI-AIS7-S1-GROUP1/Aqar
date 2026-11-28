// Original illustration of Cairo at dusk: Giza pyramids, the Citadel with the
// Muhammad Ali mosque, Cairo Tower, the New Capital's Iconic Tower, the Nile and feluccas.
// Each export is one parallax layer (same 1600x720 viewBox, stacked absolutely).
import { prng, windows } from "./prng";

const VB = "0 0 1600 720";
const svgProps = {
  viewBox: VB,
  preserveAspectRatio: "xMidYMax slice",
  className: "absolute inset-0 w-full h-full",
  "aria-hidden": true,
} as const;

export function SkyLayer() {
  const r = prng(7);
  const stars = Array.from({ length: 70 }, () => ({
    x: r() * 1600,
    y: r() * 330,
    s: r() * 1.6 + 0.4,
    d: r() * 3,
  }));
  return (
    <svg {...svgProps}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0E1116" />
          <stop offset="0.45" stopColor="#1A1823" />
          <stop offset="0.7" stopColor="#3A2230" />
          <stop offset="0.86" stopColor="#8A4636" />
          <stop offset="1" stopColor="#D88A4E" />
        </linearGradient>
        <radialGradient id="horizonGlow" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#C0644A" stopOpacity="0.55" />
          <stop offset="0.6" stopColor="#5A2E3A" stopOpacity="0.35" />
          <stop offset="1" stopColor="#3A2230" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="sunGlow" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#FFD9A0" stopOpacity="0.95" />
          <stop offset="0.35" stopColor="#F2A65A" stopOpacity="0.55" />
          <stop offset="1" stopColor="#C8372F" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="1600" height="720" fill="url(#sky)" />
      <ellipse cx="1060" cy="620" rx="520" ry="230" fill="url(#horizonGlow)" />
      {stars.map((s, i) => (
        <circle
          key={i}
          cx={s.x}
          cy={s.y}
          r={s.s}
          fill="#F4F1EA"
          className="twinkle"
          style={{ animationDelay: `${s.d}s` }}
        />
      ))}
      <g className="sun-pulse">
        <circle cx="380" cy="585" r="260" fill="url(#sunGlow)" />
        <circle cx="380" cy="585" r="72" fill="#FFD7A1" opacity="0.92" />
      </g>
      <g fill="none" stroke="#0E1116" strokeWidth="2.2" strokeLinecap="round" opacity="0.7">
        <path className="bird" d="M1500 210 q8 -8 16 0 q8 -8 16 0" />
        <path className="bird" d="M1540 240 q6 -6 12 0 q6 -6 12 0" style={{ animationDelay: "-3s" }} />
        <path className="bird bird-2" d="M1620 180 q7 -7 14 0 q7 -7 14 0" />
      </g>
    </svg>
  );
}

export function PyramidsLayer() {
  return (
    <svg {...svgProps}>
      <defs>
        <linearGradient id="pyrL" x1="0" x2="1">
          <stop offset="0" stopColor="#C98B5A" />
          <stop offset="1" stopColor="#A86A44" />
        </linearGradient>
      </defs>
      <g opacity="0.85">
        {/* Khufu */}
        <polygon points="120,610 300,430 480,610" fill="url(#pyrL)" />
        <polygon points="300,430 480,610 330,610" fill="#7E4B35" opacity="0.55" />
        {/* Khafre (keeps its casing cap) */}
        <polygon points="420,610 560,462 700,610" fill="url(#pyrL)" />
        <polygon points="560,462 700,610 585,610" fill="#7E4B35" opacity="0.55" />
        <polygon points="548,475 560,462 572,475" fill="#E6C08F" />
        {/* Menkaure */}
        <polygon points="690,610 760,540 830,610" fill="url(#pyrL)" />
        <polygon points="760,540 830,610 772,610" fill="#7E4B35" opacity="0.55" />
      </g>
      <rect x="0" y="606" width="1600" height="30" fill="#6E3F2E" opacity="0.55" />
    </svg>
  );
}

export function CitadelLayer() {
  // Muhammad Ali mosque on the Citadel hill: big dome, half domes, two pencil minarets
  return (
    <svg {...svgProps}>
      <g fill="#1A141D" transform="translate(-150 0)">
        <path d="M980 640 C 1040 590, 1120 572, 1200 570 C 1290 570, 1360 590, 1420 640 Z" />
        <rect x="1100" y="520" width="200" height="56" />
        <path d="M1150 522 a50 46 0 0 1 100 0 Z" />
        <path d="M1110 534 a28 22 0 0 1 56 0 Z" />
        <path d="M1234 534 a28 22 0 0 1 56 0 Z" />
        <path d="M1188 484 a12 12 0 0 1 24 0 Z" />
        <rect x="1197" y="470" width="6" height="16" />
        {/* minarets */}
        <rect x="1084" y="402" width="9" height="170" />
        <polygon points="1081,404 1088.5,360 1096,404" />
        <rect x="1080" y="458" width="17" height="4" />
        <rect x="1307" y="402" width="9" height="170" />
        <polygon points="1304,404 1311.5,360 1319,404" />
        <rect x="1303" y="458" width="17" height="4" />
        {/* citadel walls */}
        <rect x="1020" y="566" width="70" height="40" />
        <rect x="1320" y="566" width="70" height="40" />
        <path d="M1020 566 h70 v-6 h-8 v4 h-8 v-4 h-8 v4 h-8 v-4 h-8 v4 h-8 v-4 h-8 v4 h-8 v-4 h-6z" />
      </g>
    </svg>
  );
}

export function TowersLayer() {
  const towers = [
    { x: 560, w: 70, top: 470, seed: 11 },
    { x: 640, w: 54, top: 420, seed: 12 },
    { x: 1290, w: 80, top: 455, seed: 13 },
    { x: 880, w: 58, top: 520, seed: 14 },
    { x: 1440, w: 64, top: 480, seed: 15 },
    { x: 1520, w: 70, top: 440, seed: 16 },
  ];
  return (
    <svg {...svgProps}>
      <defs>
        <linearGradient id="iconic" x1="0" x2="1">
          <stop offset="0" stopColor="#1A1F2B" />
          <stop offset="0.55" stopColor="#2A3141" />
          <stop offset="1" stopColor="#151922" />
        </linearGradient>
      </defs>
      {/* Iconic Tower, New Administrative Capital (tapered) */}
      <g transform="translate(-200 0)">
        <polygon points="1372,640 1386,150 1394,150 1414,640" fill="url(#iconic)" />
        <rect x="1388.5" y="96" width="3" height="56" fill="#2A3141" />
        <circle cx="1390" cy="96" r="3" fill="#C8372F" className="twinkle" />
        {Array.from({ length: 22 }, (_, i) => (
          <rect key={i} x={1384 + i * 0.2} y={180 + i * 20} width={14 - i * 0.12} height="2" fill="#E9B872" opacity={i % 3 === 0 ? 0.55 : 0.18} />
        ))}
      </g>
      {towers.map((t) => (
        <g key={t.seed}>
          <rect x={t.x} y={t.top} width={t.w} height={640 - t.top} fill="#171B24" />
          {windows(t.seed, t.x + 4, t.top + 10, t.w - 8, 620 - t.top, Math.round(t.w / 14), Math.round((620 - t.top) / 16), 0.38).map(
            (w, i) =>
              w.lit && (
                <rect key={i} x={w.x} y={w.y} width={w.w} height={w.h} fill="#E9B872" opacity="0.85" className={w.flicker ? "win-flicker" : undefined} />
              )
          )}
        </g>
      ))}
      {/* Cairo Tower (lotus lattice) */}
      <g>
        <path d="M748 640 L756 330 L774 330 L782 640 Z" fill="#1E2430" />
        {Array.from({ length: 30 }, (_, i) => (
          <path key={i} d={`M${750 + (i % 2) * 2} ${630 - i * 10} l28 -6`} stroke="#2E3646" strokeWidth="1.2" />
        ))}
        <path d="M744 332 C 748 300, 782 300, 786 332 Z" fill="#232A37" />
        <path d="M740 300 Q 765 284 790 300 L786 312 Q 765 300 744 312 Z" fill="#2B3342" />
        <rect x="752" y="276" width="26" height="12" rx="2" fill="#2B3342" />
        <rect x="763.5" y="226" width="3" height="52" fill="#2B3342" />
        <circle cx="765" cy="226" r="2.6" fill="#C8372F" className="twinkle" />
        <rect x="752" y="292" width="26" height="4" fill="#E9B872" opacity="0.8" />
      </g>
    </svg>
  );
}

export function RiversideLayer() {
  const r = prng(31);
  const blocks: { x: number; w: number; h: number; seed: number }[] = [];
  let x = -20;
  while (x < 1620) {
    const w = 40 + r() * 70;
    blocks.push({ x, w, h: 34 + r() * 70, seed: Math.floor(r() * 10000) });
    x += w + 4 + r() * 10;
  }
  const palms = [80, 210, 470, 905, 1180, 1560];
  return (
    <svg {...svgProps}>
      {blocks.map((b, i) => (
        <g key={i}>
          <rect x={b.x} y={650 - b.h} width={b.w} height={b.h} fill="#11141B" />
          {windows(b.seed, b.x + 3, 655 - b.h, b.w - 6, b.h - 14, Math.max(2, Math.round(b.w / 12)), Math.max(2, Math.round(b.h / 14)), 0.32).map(
            (w, j) => w.lit && <rect key={j} x={w.x} y={w.y} width={w.w} height={w.h} fill="#F2C27E" opacity="0.75" />
          )}
        </g>
      ))}
      {palms.map((px) => (
        <g key={px} fill="#0B0D12">
          <path d={`M${px} 652 q 4 -40 2 -78 l3 0 q 2 38 -1 78 z`} />
          <path d={`M${px + 3} 574 q -26 -6 -40 8 q 22 -14 40 -4 z`} />
          <path d={`M${px + 3} 574 q 26 -6 40 8 q -22 -14 -40 -4 z`} />
          <path d={`M${px + 3} 574 q -14 -20 -34 -20 q 22 6 34 22 z`} />
          <path d={`M${px + 3} 574 q 14 -20 34 -20 q -22 6 -34 22 z`} />
          <path d={`M${px + 3} 574 q 0 -24 4 -30 q -1 16 -2 30 z`} />
        </g>
      ))}
    </svg>
  );
}

export function NileLayer() {
  return (
    <svg {...svgProps}>
      <defs>
        <linearGradient id="nile" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#3A2A33" />
          <stop offset="0.4" stopColor="#1B2B38" />
          <stop offset="1" stopColor="#0E1116" />
        </linearGradient>
      </defs>
      <rect x="0" y="650" width="1600" height="70" fill="url(#nile)" />
      {/* reflections */}
      <g stroke="#E9B872" strokeLinecap="round">
        {[
          [300, 664, 120], [330, 676, 70], [360, 688, 40], [720, 668, 60], [1380, 666, 40],
          [1100, 680, 90], [520, 698, 50], [900, 704, 70],
        ].map(([x, y, w], i) => (
          <line key={i} x1={x} y1={y} x2={x + w} y2={y} strokeWidth="2" className="water-line" style={{ animationDelay: `${i * 0.7}s` }} />
        ))}
      </g>
      {/* feluccas */}
      <g className="felucca">
        <path d="M1010 676 q 40 10 80 0 l-8 8 q -32 6 -64 0 z" fill="#0B0D12" />
        <path d="M1046 676 L1046 612" stroke="#0B0D12" strokeWidth="2" />
        <path d="M1047 614 L1088 672 L1047 672 Z" fill="#F4F1EA" opacity="0.92" />
        <path d="M1032 600 L1094 640" stroke="#0B0D12" strokeWidth="2" />
      </g>
      <g className="felucca felucca-slow">
        <path d="M560 690 q 30 8 60 0 l-6 6 q -24 5 -48 0 z" fill="#0B0D12" />
        <path d="M587 690 L587 642" stroke="#0B0D12" strokeWidth="1.6" />
        <path d="M588 644 L618 687 L588 687 Z" fill="#E9B872" opacity="0.85" />
        <path d="M576 632 L622 662" stroke="#0B0D12" strokeWidth="1.6" />
      </g>
    </svg>
  );
}

/** Cairo Tower + Nile only, compact (city card, auth pages). viewBox 400x500 */
export function MiniCairo() {
  return (
    <svg viewBox="0 0 400 500" preserveAspectRatio="xMidYMax slice" className="absolute inset-0 w-full h-full" aria-hidden>
      <defs>
        <linearGradient id="mcSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1A1823" />
          <stop offset="0.7" stopColor="#5A2E33" />
          <stop offset="1" stopColor="#D88A4E" />
        </linearGradient>
      </defs>
      <rect width="400" height="500" fill="url(#mcSky)" />
      <circle cx="110" cy="380" r="46" fill="#FFD7A1" opacity="0.85" className="sun-pulse" />
      <path d="M190 420 L196 150 L208 150 L214 420 Z" fill="#1E2430" />
      <path d="M184 150 Q 202 128 220 150 L216 160 Q 202 150 188 160 Z" fill="#2B3342" />
      <rect x="194" y="126" width="16" height="10" fill="#2B3342" />
      <rect x="201" y="88" width="2" height="40" fill="#2B3342" />
      <circle cx="202" cy="88" r="2.4" fill="#C8372F" className="twinkle" />
      {[40, 90, 250, 300, 345].map((x, i) => (
        <rect key={x} x={x} y={360 - (i % 3) * 30} width="44" height={80 + (i % 3) * 30} fill="#151922" />
      ))}
      <rect x="0" y="420" width="400" height="80" fill="#1B2B38" />
      <g className="felucca">
        <path d="M250 450 q 26 7 52 0 l-5 6 q -21 4 -42 0 z" fill="#0B0D12" />
        <path d="M274 450 L274 408" stroke="#0B0D12" strokeWidth="1.6" />
        <path d="M275 410 L300 447 L275 447 Z" fill="#F4F1EA" opacity="0.9" />
      </g>
      <line x1="90" y1="440" x2="150" y2="440" stroke="#E9B872" strokeWidth="2" className="water-line" />
      <line x1="120" y1="460" x2="160" y2="460" stroke="#E9B872" strokeWidth="2" className="water-line" style={{ animationDelay: "1s" }} />
    </svg>
  );
}
