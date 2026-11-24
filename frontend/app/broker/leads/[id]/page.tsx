import Link from "next/link";

export default function LeadDetailPage() {
  return (
    <div className="min-h-screen bg-paper text-ink flex flex-col">
      {/* Header (ink) */}
      <header className="bg-ink text-paper px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/broker" className="text-xl font-[900] tracking-tight text-paper">
            AqarAI
          </Link>
          <span className="text-sm text-muted-dark">/ ملخص العميل</span>
        </div>

        <Link
          href="/broker"
          className="text-xs font-bold text-muted-dark hover:text-paper transition-colors duration-200"
        >
          رجوع للقائمة
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-line/40">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-[900] text-ink">ملخص العميل</h1>
            <span className="bg-hot text-paper text-xs font-bold px-3 py-1 rounded-full">
              Hot · 92
            </span>
            <span className="bg-[#E4E1D8] text-[#3F3F3A] text-xs font-bold px-3 py-1 rounded-full">
              الـ AI شغال
            </span>
          </div>

          <div className="border border-dashed border-line/60 rounded-xl px-4 py-2 text-xs text-muted">
            منطقة التحكم والتدخل (Sprint 3)
          </div>
        </div>

        <div className="mt-6 bg-sand p-8 rounded-2xl border border-line/40 text-center">
          <h2 className="text-lg font-bold text-ink">تفاصيل الـ Lead Brief</h2>
          <p className="mt-1 text-sm text-muted">
            شاشة ملخص العميل والوحدات المقترحة لشركة الوساطة (Lead Page)
          </p>
        </div>
      </main>
    </div>
  );
}
