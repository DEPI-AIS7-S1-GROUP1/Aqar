import type { Metadata } from "next";
import { Noto_Kufi_Arabic } from "next/font/google";
import "./globals.css";

const notoKufiArabic = Noto_Kufi_Arabic({
  subsets: ["arabic"],
  weight: ["400", "700", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AqarAI | عقار",
  description: "يفهم العميل. يتأكد إنه يقدر يدفع. يسلّمه للوسيط جاهز.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`${notoKufiArabic.className} antialiased bg-ink`}>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:right-3 focus:z-50 focus:bg-paper focus:text-ink focus:px-4 focus:py-2 focus:rounded-full"
        >
          تخطي للمحتوى
        </a>
        <div id="main-content">{children}</div>
      </body>
    </html>
  );
}
