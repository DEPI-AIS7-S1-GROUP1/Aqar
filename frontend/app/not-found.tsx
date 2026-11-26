import Link from "next/link";
import { MiniPyramids } from "@/components/scenes/MiniScenes";

export default function NotFound() {
  return (
    <main className="relative min-h-[100svh] bg-ink text-paper overflow-hidden flex items-center justify-center px-5">
      <div className="absolute inset-0 opacity-40">
        <MiniPyramids />
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/70 to-ink/40" />
      <div className="relative text-center max-w-md">
        <p className="text-[120px] sm:text-[160px] font-[900] leading-none text-paper/10">٤٠٤</p>
        <h1 className="-mt-6 text-3xl font-[900]">الصفحة دي مش موجودة</h1>
        <p className="mt-3 text-muted-dark">يمكن اللينك اتغير، أو الصفحة لسه بتتبني.</p>
        <Link href="/" className="mt-8 inline-block bg-accent px-7 py-3.5 rounded-full font-bold hover:-translate-y-[2px] transition-transform">
          ارجع للرئيسية
        </Link>
      </div>
    </main>
  );
}
