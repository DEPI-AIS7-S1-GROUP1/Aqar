export default function RotatingRing({ text = "مساعد مبيعات عقاري ● بالعامية المصرية ● " }: { text?: string }) {
  return (
    <div className="relative w-44 h-44 flex items-center justify-center">
      <svg viewBox="0 0 200 200" className="w-full h-full animate-spin-slow" aria-hidden>
        <defs>
          <path id="ringPath" d="M 100, 100 m -72, 0 a 72,72 0 1,1 144,0 a 72,72 0 1,1 -144,0" />
        </defs>
        <text fill="#B9B6AE" fontSize="13" fontWeight="700" letterSpacing="1.2">
          <textPath href="#ringPath" startOffset="0%">
            {text}
          </textPath>
        </text>
      </svg>
      <div className="absolute w-14 h-14 rounded-full border border-paper/20 flex items-center justify-center">
        <div className="w-3 h-3 rounded-full bg-accent pulse-ring" />
      </div>
    </div>
  );
}
