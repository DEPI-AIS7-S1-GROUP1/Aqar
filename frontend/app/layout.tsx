import type { Metadata } from "next";
import { Noto_Sans_Arabic } from "next/font/google";
import "./globals.css";

const notoSansArabic = Noto_Sans_Arabic({
  subsets: ["arabic"],
});

export const metadata: Metadata = {
  title: "AqarAI",
  description: "AI sales assistant for Egyptian real estate brokerage",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className={notoSansArabic.className}>{children}</body>
    </html>
  );
}
