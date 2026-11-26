import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="bg-ink text-muted-dark border-t border-paper/10">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 py-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 text-sm">
        <div>
          <p className="text-paper text-xl font-[900]">
            AqarAI <span className="text-accent">.</span>
          </p>
          <p className="mt-1 text-xs">مشروع تخرج · DEPI · بيانات الوحدات تجريبية للعرض.</p>
        </div>
        <nav className="flex flex-wrap gap-x-6 gap-y-2 font-bold">
          <Link href="/listings" className="hover:text-paper">الوحدات</Link>
          <Link href="/chat" className="hover:text-paper">المساعد</Link>
          <Link href="/login" className="hover:text-paper">دخول الوسطاء</Link>
        </nav>
        <p className="text-xs">&copy; 2026 AqarAI</p>
      </div>
    </footer>
  );
}
