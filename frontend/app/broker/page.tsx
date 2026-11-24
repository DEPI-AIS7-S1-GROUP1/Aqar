import Link from "next/link";

export default function BrokerPage() {
  return (
    <div className="min-h-screen bg-paper text-ink flex flex-col">
      {/* Top bar (ink) */}
      <header className="bg-ink text-paper px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-xl font-[900] tracking-tight text-paper">
            AqarAI
          </Link>
          <nav className="flex items-center gap-4 text-sm font-bold">
            <span className="text-paper border-b-2 border-accent pb-1">العملاء</span>
            <span className="text-muted-dark hover:text-paper cursor-pointer">التحليلات</span>
          </nav>
        </div>

        <Link
          href="/"
          className="text-xs font-bold text-muted-dark hover:text-paper transition-colors duration-200"
        >
          الرئيسية
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 sm:p-8">
        <div className="mb-6">
          <h1 className="text-2xl font-[900] text-ink">العملاء</h1>
          <p className="text-sm text-muted">مرتبين من الأعلى تقييمًا</p>
        </div>

        <div className="bg-sand p-8 rounded-2xl border border-line/40 text-center">
          <h2 className="text-lg font-bold text-ink">لوحة الوسيط</h2>
          <p className="mt-1 text-sm text-muted">
            شاشة قائمة العملاء والتقييم المباشر (Broker Leads)
          </p>
        </div>
      </main>
    </div>
  );
}
