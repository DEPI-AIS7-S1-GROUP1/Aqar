const ROW_A = ["القاهرة الجديدة", "الشيخ زايد", "6 أكتوبر", "العاصمة الإدارية", "مستقبل سيتي", "الساحل الشمالي"];
const ROW_B = ["مقدم يناسبك", "قسط يريحك", "دفعة استلام واضحة", "مقارنة خطط السداد", "وسيط معاه ملفك"];

function Row({ items, reverse = false, accent = false }: { items: string[]; reverse?: boolean; accent?: boolean }) {
  const seq = [...items, ...items, ...items, ...items];
  return (
    <div className="marquee-wrap overflow-hidden" dir="ltr">
      <div className={`flex w-max gap-10 whitespace-nowrap ${reverse ? "marquee-rev" : "marquee"}`}>
        {seq.map((t, i) => (
          <span
            key={i}
            dir="rtl"
            className={`flex items-center gap-10 text-3xl sm:text-5xl font-[900] tracking-tight ${
              accent ? "text-transparent [-webkit-text-stroke:1px_#B9B6AE]" : "text-paper"
            }`}
          >
            {t}
            <span className="w-3 h-3 rounded-full bg-accent inline-block" aria-hidden />
          </span>
        ))}
      </div>
    </div>
  );
}

export default function AreaMarquee() {
  return (
    <section aria-label="المناطق اللي بنغطيها" className="bg-ink py-12 sm:py-16 flex flex-col gap-6 border-y border-paper/10">
      <Row items={ROW_A} />
      <Row items={ROW_B} reverse accent />
    </section>
  );
}
