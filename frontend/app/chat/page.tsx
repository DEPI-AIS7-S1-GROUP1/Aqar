import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-sand flex flex-col">
      {/* Header (ink) */}
      <header className="bg-ink text-paper px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-accent text-paper font-bold flex items-center justify-center">
            A
          </div>
          <div>
            <h1 className="text-base font-bold text-paper">مساعد AqarAI</h1>
            <p className="text-xs text-muted-dark">متاح دلوقتي</p>
          </div>
        </div>

        <Link
          href="/"
          className="text-xs font-bold text-muted-dark hover:text-paper transition-colors duration-200"
        >
          الرئيسية
        </Link>
      </header>

      {/* Message area (sand) */}
      <main className="flex-1 max-w-xl w-full mx-auto p-6 flex flex-col justify-center items-center text-center">
        <div className="bg-paper p-8 rounded-2xl shadow-sm border border-line/30 max-w-md w-full">
          <h2 className="text-xl font-[900] text-ink">محادثة العميل</h2>
          <p className="mt-2 text-sm text-muted">
            شاشة المحادثة بالعامية المصرية (Customer Chat)
          </p>
        </div>
      </main>
    </div>
  );
}
