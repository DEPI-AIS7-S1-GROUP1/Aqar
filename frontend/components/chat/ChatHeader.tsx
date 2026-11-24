import Link from "next/link";

export default function ChatHeader() {
  return (
    <header className="sticky top-0 z-20 w-full bg-ink text-paper px-4 py-3 sm:px-6 sm:py-3.5 shadow-sm border-b border-line/20">
      <div className="max-w-3xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full bg-accent text-paper font-bold flex items-center justify-center text-lg select-none shadow-sm"
            aria-hidden="true"
          >
            A
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-paper leading-tight">
              مساعد AqarAI
            </h1>
            <div className="flex items-center gap-1.5 text-xs text-muted-dark mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" />
              <span>متاح دلوقتي</span>
            </div>
          </div>
        </div>

        <Link
          href="/"
          className="text-xs sm:text-sm font-bold text-muted-dark hover:text-paper transition-colors duration-200 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-paper/10 px-2"
          aria-label="الرجوع إلى الصفحة الرئيسية"
        >
          الرئيسية
        </Link>
      </div>
    </header>
  );
}
