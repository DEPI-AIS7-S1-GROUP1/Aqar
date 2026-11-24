import Link from "next/link";
import Image from "next/image";

export default function HomePage() {
  return (
    <div className="relative min-h-screen bg-ink text-paper flex flex-col justify-between overflow-hidden select-none">
      {/* Giant faint Arabic word behind everything */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-10 sm:-top-20 left-1/2 -translate-x-1/2 text-[180px] sm:text-[320px] lg:text-[460px] font-[900] text-paper/[0.05] leading-none select-none z-0"
      >
        عقار
      </div>

      {/* Top navigation bar */}
      <header className="relative z-10 w-full px-5 sm:px-8 lg:px-12 pt-6 pb-4">
        <nav className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <Link
            href="/"
            className="text-2xl font-[900] tracking-tight text-paper transition-transform duration-200 hover:-translate-y-[2px]"
          >
            AqarAI
          </Link>

          <div className="hidden md:flex items-center gap-8 text-sm font-bold text-muted-dark">
            <Link
              href="/"
              className="text-paper transition-colors duration-200 hover:text-accent"
            >
              الرئيسية
            </Link>
            <Link
              href="#how-it-works"
              className="transition-colors duration-200 hover:text-paper"
            >
              إزاي بيشتغل
            </Link>
            <Link
              href="#units"
              className="transition-colors duration-200 hover:text-paper"
            >
              الوحدات
            </Link>
            <Link
              href="/broker"
              className="transition-colors duration-200 hover:text-paper"
            >
              لوحة الوسيط
            </Link>
          </div>

          <Link
            href="/chat"
            className="bg-paper text-ink text-sm font-bold px-5 py-2.5 rounded-full transition-all duration-200 hover:bg-accent hover:text-paper hover:-translate-y-[2px] shadow-sm"
          >
            ابدأ المحادثة
          </Link>
        </nav>
      </header>

      {/* Main hero area */}
      <main className="relative z-10 flex-1 flex flex-col justify-center px-5 sm:px-8 lg:px-12 py-10 sm:py-16">
        <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Headline and CTAs (right side in RTL) */}
          <div className="lg:col-span-8 z-10">
            <h1 className="text-3xl sm:text-5xl lg:text-[64px] font-[900] leading-[1.18] text-paper tracking-tight">
              يفهم العميل.
              <br />
              يتأكد إنه يقدر يدفع.
              <br />
              يسلّمه للوسيط جاهز.
            </h1>

            <p className="mt-6 text-base sm:text-[18px] text-muted-dark max-w-2xl leading-relaxed">
              أول مساعد مبيعات ذكي لشركات الوساطة العقارية في مصر — يتكلم مع
              المشتري بالعامية المصرية، يراجع ميزانيته وخطط السداد، ويحوّله
              لموظف المبيعات مع ملخص كامل.
            </p>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link
                href="/chat"
                className="bg-accent text-paper font-bold text-base px-8 py-3.5 rounded-full transition-transform duration-200 hover:-translate-y-[2px] shadow-lg shadow-accent/20"
              >
                جرّب المحادثة
              </Link>
              <Link
                href="/broker"
                className="border border-line/40 text-paper font-bold text-base px-8 py-3.5 rounded-full transition-all duration-200 hover:border-paper hover:-translate-y-[2px]"
              >
                شوف لوحة الوسيط
              </Link>
            </div>

            {/* Three step chips */}
            <div className="mt-10 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-full border border-line/20 bg-ink/70 px-4 py-1.5 text-xs sm:text-sm font-medium text-muted-dark backdrop-blur-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                التأهيل
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-line/20 bg-ink/70 px-4 py-1.5 text-xs sm:text-sm font-medium text-muted-dark backdrop-blur-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-line/60" />
                البحث والمطابقة
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-line/20 bg-ink/70 px-4 py-1.5 text-xs sm:text-sm font-medium text-muted-dark backdrop-blur-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-line/60" />
                التسليم للموظف
              </span>
            </div>
          </div>

          {/* Rotating text ring */}
          <div className="hidden lg:flex lg:col-span-4 justify-center items-center relative z-10">
            <div className="relative w-48 h-48 sm:w-56 sm:h-56 flex items-center justify-center">
              <svg
                viewBox="0 0 200 200"
                className="w-full h-full animate-spin-slow"
                aria-hidden="true"
              >
                <defs>
                  <path
                    id="circlePath"
                    d="M 100, 100 m -70, 0 a 70,70 0 1,1 140,0 a 70,70 0 1,1 -140,0"
                  />
                </defs>
                <text
                  fill="#B9B6AE"
                  fontSize="12.5"
                  fontWeight="700"
                  letterSpacing="1.5"
                >
                  <textPath href="#circlePath" startOffset="0%">
                    مساعد مبيعات عقاري ● بالعامية المصرية ●
                  </textPath>
                </text>
              </svg>
              {/* Center icon / dot */}
              <div className="absolute w-3 h-3 rounded-full bg-accent" />
            </div>
          </div>
        </div>
      </main>

      {/* Building drawing: bottom-left, absolute, width 780px (max 62%) */}
      <div className="pointer-events-none absolute bottom-0 left-0 w-[320px] sm:w-[520px] lg:w-[780px] max-w-[62%] z-0 select-none animate-building-drift opacity-85 lg:opacity-100">
        <Image
          src="/hero-building.svg"
          alt="رسم مبنى معاصر"
          width={780}
          height={550}
          className="w-full h-auto object-contain"
          priority
        />
      </div>

      {/* Bottom bar & red scroll circle */}
      <footer className="relative z-10 w-full px-5 sm:px-8 lg:px-12 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Red scroll circle bottom-left */}
          <a
            href="#how-it-works"
            aria-label="انتقل للأسفل"
            className="w-10 h-10 rounded-full bg-accent flex items-center justify-center text-paper shadow-md transition-transform duration-200 hover:-translate-y-[2px] animate-scroll-bob"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 14l-7 7m0 0l-7-7m7 7V3"
              />
            </svg>
          </a>
          <span className="hidden sm:inline text-xs text-muted-dark">
            اكتشف المزيد
          </span>
        </div>

        <p className="text-xs text-muted-dark">
          جميع الحقوق محفوظة &copy; 2026 AqarAI
        </p>
      </footer>
    </div>
  );
}
