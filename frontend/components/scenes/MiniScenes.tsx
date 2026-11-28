// Small original scenes (viewBox 400x500) for the city cards and auth pages.

const P = {
  viewBox: "0 0 400 500",
  preserveAspectRatio: "xMidYMax slice",
  className: "absolute inset-0 w-full h-full",
  "aria-hidden": true,
} as const;

/** West Cairo (Sheikh Zayed / October): the pyramids at golden hour. */
export function MiniPyramids() {
  return (
    <svg {...P}>
      <defs>
        <linearGradient id="mpSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2A1E2A" />
          <stop offset="0.6" stopColor="#A0553C" />
          <stop offset="1" stopColor="#F0B56E" />
        </linearGradient>
        <linearGradient id="mpSand" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#C68A55" />
          <stop offset="1" stopColor="#7B4A31" />
        </linearGradient>
      </defs>
      <rect width="400" height="500" fill="url(#mpSky)" />
      <circle cx="300" cy="300" r="40" fill="#FFE0AE" className="sun-pulse" />
      <polygon points="20,420 150,270 280,420" fill="#B97A4C" />
      <polygon points="150,270 280,420 170,420" fill="#7E4B35" opacity="0.55" />
      <polygon points="220,420 300,330 380,420" fill="#B97A4C" />
      <polygon points="300,330 380,420 312,420" fill="#7E4B35" opacity="0.55" />
      <polygon points="292,339 300,330 308,339" fill="#EBC896" />
      <path d="M0 420 Q 200 395 400 420 L400 500 L0 500 Z" fill="url(#mpSand)" />
      <g className="float-y" fill="#2B1B18">
        <rect x="60" y="400" width="34" height="14" rx="6" />
        <rect x="88" y="390" width="6" height="16" />
        <rect x="64" y="414" width="3" height="16" />
        <rect x="88" y="414" width="3" height="16" />
      </g>
    </svg>
  );
}

/** New Administrative Capital: the Iconic Tower and a modern skyline. */
export function MiniCapital() {
  return (
    <svg {...P}>
      <defs>
        <linearGradient id="mkSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0F1A2A" />
          <stop offset="1" stopColor="#3B6E8F" />
        </linearGradient>
      </defs>
      <rect width="400" height="500" fill="url(#mkSky)" />
      {[30, 70, 110, 150].map((y) => (
        <circle key={y} cx={(y * 7) % 400} cy={y} r="1.2" fill="#fff" className="twinkle" style={{ animationDelay: `${y / 50}s` }} />
      ))}
      <polygon points="190,470 198,70 204,70 214,470" fill="#1B2638" />
      <rect x="200" y="36" width="2" height="36" fill="#1B2638" />
      <circle cx="201" cy="36" r="2.6" fill="#C8372F" className="twinkle" />
      {Array.from({ length: 18 }, (_, i) => (
        <rect key={i} x={197} y={100 + i * 20} width={10} height="1.6" fill="#9ED0F0" opacity={i % 2 ? 0.25 : 0.6} />
      ))}
      {[
        [20, 330, 50], [80, 300, 46], [130, 360, 40], [240, 320, 48], [295, 280, 44], [345, 350, 50],
      ].map(([x, y, w]) => (
        <g key={x}>
          <rect x={x} y={y} width={w} height={470 - y} fill="#152031" />
          {Array.from({ length: Math.floor((470 - y) / 18) }, (_, j) => (
            <rect key={j} x={x + 6} y={y + 8 + j * 18} width={w - 12} height="3" fill="#9ED0F0" opacity={(j + x) % 3 === 0 ? 0.6 : 0.15} />
          ))}
        </g>
      ))}
      <rect x="0" y="470" width="400" height="30" fill="#0E1116" />
    </svg>
  );
}

/** North Coast / Mediterranean: sea, sun, waves, umbrellas. */
export function MiniCoast() {
  return (
    <svg {...P}>
      <defs>
        <linearGradient id="mcoSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#7CC3D9" />
          <stop offset="1" stopColor="#E9F4F2" />
        </linearGradient>
        <linearGradient id="mcoSea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1C8AA6" />
          <stop offset="1" stopColor="#0F5A73" />
        </linearGradient>
      </defs>
      <rect width="400" height="500" fill="url(#mcoSky)" />
      <circle cx="90" cy="120" r="34" fill="#FFF1C9" className="sun-pulse" />
      <rect x="0" y="260" width="400" height="140" fill="url(#mcoSea)" />
      <g className="wave" fill="none" stroke="#E9F4F2" strokeWidth="2.4" opacity="0.8">
        <path d="M0 300 q 25 -10 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0" />
      </g>
      <g className="wave wave-2" fill="none" stroke="#BDE6EE" strokeWidth="2" opacity="0.7">
        <path d="M-100 340 q 25 -10 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0 t 50 0" />
      </g>
      <path d="M0 390 Q 200 370 400 392 L400 500 L0 500 Z" fill="#F3E2C0" />
      {[
        [90, "#C8372F"], [210, "#F4F1EA"], [320, "#2F5D8C"],
      ].map(([x, c]) => (
        <g key={x as number}>
          <rect x={(x as number) - 1} y="400" width="2.4" height="56" fill="#6B5B4B" />
          <path d={`M${(x as number) - 34} 404 Q ${x} 370 ${(x as number) + 34} 404 Z`} fill={c as string} />
        </g>
      ))}
      <g className="felucca">
        <path d="M280 268 l 10 -44 l 14 44 z" fill="#fff" />
        <path d="M274 270 h 40 l -6 6 h -28 z" fill="#0E1116" />
      </g>
    </svg>
  );
}

/** Alexandria by night: Qaitbay citadel, the old lighthouse beam, Corniche lights. viewBox 800x900 */
export function AlexandriaNight() {
  return (
    <svg viewBox="0 0 800 900" preserveAspectRatio="xMidYMax slice" className="absolute inset-0 w-full h-full" aria-hidden>
      <defs>
        <linearGradient id="axSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0B1220" />
          <stop offset="0.7" stopColor="#1C2B44" />
          <stop offset="1" stopColor="#35506F" />
        </linearGradient>
        <linearGradient id="axSea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1A2F48" />
          <stop offset="1" stopColor="#0B1220" />
        </linearGradient>
        <linearGradient id="axBeam" x1="1" y1="0" x2="0" y2="0">
          <stop offset="0" stopColor="#FFE7B0" stopOpacity="0.8" />
          <stop offset="1" stopColor="#FFE7B0" stopOpacity="0" />
        </linearGradient>
      </defs>
      <rect width="800" height="900" fill="url(#axSky)" />
      {Array.from({ length: 40 }, (_, i) => (
        <circle key={i} cx={(i * 197) % 800} cy={(i * 89) % 420} r={(i % 3) * 0.6 + 0.6} fill="#fff" className="twinkle" style={{ animationDelay: `${(i % 7) * 0.4}s` }} />
      ))}
      <circle cx="640" cy="150" r="38" fill="#F4F1EA" opacity="0.9" />
      <circle cx="626" cy="140" r="38" fill="#0B1220" opacity="0.9" />
      {/* lighthouse beam (nod to the Pharos that stood here) */}
      <polygon className="lighthouse-beam" points="-200,380 470,474 470,486 -200,560" fill="url(#axBeam)" />
      {/* Qaitbay citadel */}
      <g fill="#0F1826">
        <path d="M250 700 L250 620 L560 620 L560 700 Z" />
        <rect x="330" y="530" width="150" height="100" />
        <rect x="380" y="470" width="50" height="62" />
        <rect x="396" y="456" width="18" height="16" />
        <path d="M402 456 L405 440 L408 456 Z" />
        {Array.from({ length: 16 }, (_, i) => (
          <rect key={i} x={250 + i * 20} y="610" width="10" height="10" />
        ))}
        {Array.from({ length: 8 }, (_, i) => (
          <rect key={`t${i}`} x={330 + i * 19} y="521" width="10" height="10" />
        ))}
        <circle cx="250" cy="640" r="26" />
        <circle cx="560" cy="640" r="26" />
        <circle cx="330" cy="560" r="18" />
        <circle cx="480" cy="560" r="18" />
      </g>
      <g fill="#E9B872">
        <rect x="397" y="490" width="6" height="12" rx="3" opacity="0.9" />
        <rect x="360" y="575" width="6" height="12" rx="3" opacity="0.6" />
        <rect x="440" y="575" width="6" height="12" rx="3" opacity="0.6" />
        <circle cx="405" cy="480" r="5" className="twinkle" />
      </g>
      <rect x="0" y="700" width="800" height="200" fill="url(#axSea)" />
      {/* Corniche lights */}
      <path d="M560 760 Q 700 740 820 700" stroke="#E9B872" strokeWidth="2" strokeDasharray="2 10" fill="none" opacity="0.8" />
      <g className="wave" fill="none" stroke="#6E8FB3" strokeWidth="2" opacity="0.5">
        <path d="M0 760 q 30 -10 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0" />
      </g>
      <g className="wave wave-2" fill="none" stroke="#4C6B8F" strokeWidth="2" opacity="0.5">
        <path d="M-200 820 q 30 -10 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0" />
      </g>
      <line x1="380" y1="730" x2="430" y2="730" stroke="#E9B872" strokeWidth="2" className="water-line" />
      <line x1="395" y1="750" x2="420" y2="750" stroke="#E9B872" strokeWidth="2" className="water-line" style={{ animationDelay: "1.3s" }} />
    </svg>
  );
}
