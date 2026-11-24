import Link from "next/link";

export default function BrokerHeader() {
  return (
    <header className="w-full bg-ink text-paper px-4 sm:px-8 py-3.5 border-b border-line/20 shadow-sm">
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-6 sm:gap-10">
          <Link
            href="/"
            className="text-xl sm:text-2xl font-[900] tracking-tight text-paper transition-transform duration-200 hover:-translate-y-[2px]"
          >
            AqarAI
          </Link>

          {/* Navigation tabs */}
          <nav className="flex items-center gap-6 text-sm font-bold">
            <span
              className="relative py-2 text-paper border-b-2 border-accent cursor-default"
              aria-current="page"
            >
              العملاء
            </span>
            <button
              disabled
              title="Sprint 3"
              className="py-2 text-muted-dark opacity-50 cursor-not-allowed hover:text-muted-dark flex items-center gap-1.5"
            >
              التحليلات
              <span className="text-[10px] bg-paper/10 px-1.5 py-0.5 rounded font-normal">
                Sprint 3
              </span>
            </button>
          </nav>
        </div>

        <Link
          href="/"
          className="text-xs sm:text-sm text-muted-dark hover:text-paper transition-colors duration-200"
        >
          الرئيسية
        </Link>
      </div>
    </header>
  );
}
