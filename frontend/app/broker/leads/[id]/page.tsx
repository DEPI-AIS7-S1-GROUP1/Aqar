import Link from "next/link";
import BandBadge from "@/components/ui/BandBadge";
import ModeBadge from "@/components/ui/ModeBadge";
import AffordabilityBadge from "@/components/ui/AffordabilityBadge";
import { SAMPLE_LEAD_DETAILS, formatValue } from "@/lib/sample-data";

export function generateStaticParams() {
  return Object.keys(SAMPLE_LEAD_DETAILS).map((id) => ({ id }));
}

interface LeadDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: LeadDetailPageProps) {
  const { id } = await params;

  // Retrieve lead detail from sample data
  const lead = SAMPLE_LEAD_DETAILS[id];

  // If lead is unknown, show simple "العميل مش موجود" page
  if (!lead) {
    return (
      <div className="min-h-screen bg-sand flex flex-col justify-between">
        <header className="w-full bg-ink text-paper px-4 sm:px-8 py-3.5 border-b border-line/20 shadow-sm">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <Link
              href="/broker"
              className="text-xl sm:text-2xl font-[900] tracking-tight text-paper"
            >
              AqarAI
            </Link>
            <Link
              href="/broker"
              className="text-xs sm:text-sm text-muted-dark hover:text-paper"
            >
              رجوع للعملاء
            </Link>
          </div>
        </header>

        <main className="flex-1 max-w-md w-full mx-auto px-4 py-16 flex flex-col justify-center items-center text-center">
          <div className="bg-white border border-line/40 rounded-2xl p-8 w-full shadow-sm">
            <div className="w-12 h-12 rounded-full bg-sand flex items-center justify-center mx-auto mb-4 text-ink font-bold text-xl">
              !
            </div>
            <h1 className="text-xl font-[900] text-ink">العميل مش موجود</h1>
            <p className="mt-2 text-sm text-muted leading-relaxed">
              لم يتم العثور على بيانات تفصيلية للعميل رقم ({id}) في النظام
              حالياً.
            </p>
            <Link
              href="/broker"
              className="mt-6 inline-block bg-ink text-paper px-6 py-2.5 rounded-full text-sm font-bold hover:bg-accent transition-colors shadow-sm"
            >
              الرجوع إلى قائمة العملاء
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sand flex flex-col">
      {/* Top navigation header */}
      <header className="w-full bg-ink text-paper px-4 sm:px-8 py-3.5 border-b border-line/20 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link
              href="/broker"
              className="text-xl sm:text-2xl font-[900] tracking-tight text-paper transition-transform duration-200 hover:-translate-y-[2px]"
            >
              AqarAI
            </Link>
            <span className="text-muted-dark text-xs sm:text-sm">
              / ملخص العميل
            </span>
          </div>

          <Link
            href="/broker"
            className="text-xs sm:text-sm font-bold text-muted-dark hover:text-paper transition-colors duration-200"
          >
            ← رجوع لقائمة العملاء
          </Link>
        </div>
      </header>

      {/* Main page container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-8 py-8 flex flex-col gap-6">
        {/* Lead brief top bar */}
        <div className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-[900] text-ink tracking-tight">
              عميل {lead.lead_id}
            </h1>
            <BandBadge band={lead.band} score={lead.score} />
            <ModeBadge mode={lead.mode || "AI_ACTIVE"} />
          </div>

          {/* Reserved takeover buttons box (Sprint 3) */}
          <div className="border-2 border-dashed border-line/60 rounded-xl px-4 py-2.5 text-xs font-bold text-muted bg-sand/30 text-center select-none">
            مكان أزرار استلام المحادثة (Sprint 3)
          </div>
        </div>

        {/* Two columns layout: stack on mobile (<900px), 2 columns on desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Main Column (lg:col-span-7) */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            {/* Summary card */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <h2 className="text-base sm:text-lg font-[900] text-ink pb-3 border-b border-line/30">
                الملخص التنفيذي
              </h2>

              <div className="mt-4 flex flex-col gap-3">
                <div className="text-xs text-muted">
                  <span className="font-bold text-ink">سبب التحويل: </span>
                  <span>{formatValue(lead.trigger)}</span>
                </div>

                <p className="text-sm sm:text-base text-ink leading-relaxed bg-sand/40 p-4 rounded-xl border border-line/20">
                  {formatValue(lead.summary_text)}
                </p>

                {lead.transcript_url && (
                  <div className="pt-2">
                    <Link
                      href={lead.transcript_url}
                      className="text-xs font-bold text-accent hover:underline inline-flex items-center gap-1"
                    >
                      سجل المحادثة الكاملة مع العميل ←
                    </Link>
                  </div>
                )}
              </div>
            </section>

            {/* Suggested units card */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-line/30">
                <h2 className="text-base sm:text-lg font-[900] text-ink">
                  الوحدات المقترحة ({lead.matched_units.length})
                </h2>
                <span className="text-xs text-muted">ترشيحات مطابقة</span>
              </div>

              {lead.matched_units.length > 0 ? (
                <div className="mt-4 flex flex-col gap-3.5">
                  {lead.matched_units.map((unit, index) => (
                    <div
                      key={`${unit.listing_id}-${index}`}
                      className="border border-line/40 rounded-xl p-4 bg-paper/30 flex flex-col gap-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-bold text-sm sm:text-base text-ink">
                          {unit.title || `وحدة رقم ${unit.listing_id}`}
                        </span>
                        <AffordabilityBadge status={unit.affordability} />
                      </div>

                      {unit.price_egp && (
                        <div className="text-sm font-[900] text-ink">
                          {unit.price_egp.toLocaleString("ar-EG")} جنيه
                        </div>
                      )}

                      {unit.plan_summary && (
                        <p className="text-xs text-muted leading-relaxed">
                          {unit.plan_summary}
                        </p>
                      )}

                      <div className="mt-1 pt-2 border-t border-line/20 flex items-center justify-between text-[11px] text-muted">
                        <span>خطة السداد: {unit.plan_id}</span>
                        <span>
                          رأي العميل:{" "}
                          {unit.liked === true
                            ? "أعجبته 👍"
                            : unit.liked === false
                            ? "لم تناسبه 👎"
                            : "غير متوفر"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-xs sm:text-sm text-muted bg-sand/30 p-4 rounded-xl text-center">
                  لا توجد وحدات مقترحة مسجلة حالياً لهذا العميل
                </p>
              )}
            </section>

            {/* Open questions card */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <h2 className="text-base sm:text-lg font-[900] text-ink pb-3 border-b border-line/30">
                أسئلة مفتوحة للموظف
              </h2>

              {lead.open_questions.length > 0 ? (
                <ul className="mt-4 flex flex-col gap-2.5 text-xs sm:text-sm text-ink list-disc list-inside">
                  {lead.open_questions.map((q, idx) => (
                    <li key={idx} className="leading-relaxed">
                      {q}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-xs sm:text-sm text-muted bg-sand/30 p-4 rounded-xl text-center">
                  لا توجد أسئلة مفتوحة متبقية
                </p>
              )}
            </section>
          </div>

          {/* Side Column (lg:col-span-5) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Confirmed requirements card */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <h2 className="text-base sm:text-lg font-[900] text-ink pb-3 border-b border-line/30">
                المتطلبات المؤكدة
              </h2>

              <dl className="mt-4 flex flex-col gap-3 text-xs sm:text-sm">
                <div className="flex items-center justify-between pb-2 border-b border-line/20">
                  <dt className="text-muted">المناطق المطلوبة:</dt>
                  <dd className="font-bold text-ink">
                    {formatValue(lead.confirmed.areas)}
                  </dd>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-line/20">
                  <dt className="text-muted">المقدم المتاح:</dt>
                  <dd className="font-bold text-ink">
                    {lead.confirmed.down_payment_available_egp !== null &&
                    lead.confirmed.down_payment_available_egp !== undefined
                      ? `${lead.confirmed.down_payment_available_egp.toLocaleString(
                          "ar-EG"
                        )} جنيه`
                      : "غير متوفر"}
                  </dd>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-line/20">
                  <dt className="text-muted">القدرة الشهرية:</dt>
                  <dd className="font-bold text-ink">
                    {lead.confirmed.monthly_capacity_egp !== null &&
                    lead.confirmed.monthly_capacity_egp !== undefined
                      ? `${lead.confirmed.monthly_capacity_egp.toLocaleString(
                          "ar-EG"
                        )} جنيه / شهر`
                      : "غير متوفر"}
                  </dd>
                </div>

                <div className="flex items-center justify-between pb-2 border-b border-line/20">
                  <dt className="text-muted">الجدول الزمني (Timeline):</dt>
                  <dd className="font-bold text-ink">
                    {formatValue(lead.confirmed.timeline)}
                  </dd>
                </div>

                <div className="flex items-center justify-between">
                  <dt className="text-muted">الغرض من الشراء:</dt>
                  <dd className="font-bold text-ink">
                    {lead.confirmed.purpose === "live"
                      ? "سكن شخصي"
                      : lead.confirmed.purpose === "invest"
                      ? "استثمار عقاري"
                      : formatValue(lead.confirmed.purpose)}
                  </dd>
                </div>
              </dl>
            </section>

            {/* Unconfirmed slots card */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <h2 className="text-base sm:text-lg font-[900] text-ink pb-3 border-b border-line/30">
                البيانات غير المؤكدة
              </h2>

              {lead.unconfirmed.length > 0 ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {lead.unconfirmed.map((slot) => (
                    <span
                      key={slot}
                      className="bg-sand text-muted px-3 py-1 rounded-full text-xs font-medium border border-line/30"
                    >
                      {slot}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="mt-4 text-xs text-muted bg-sand/30 p-3 rounded-xl text-center">
                  تم تأكيد جميع البيانات الأساسية
                </p>
              )}
            </section>

            {/* "ليه التقييم" score reasons list */}
            <section className="bg-white border border-line/40 rounded-2xl p-5 sm:p-6 shadow-sm">
              <h2 className="text-base sm:text-lg font-[900] text-ink pb-3 border-b border-line/30">
                ليه التقييم؟
              </h2>

              {lead.reasons.length > 0 ? (
                <ul className="mt-4 flex flex-col gap-2.5 text-xs sm:text-sm text-ink list-disc list-inside">
                  {lead.reasons.map((reason, idx) => (
                    <li key={idx} className="leading-relaxed">
                      {reason}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-xs text-muted bg-sand/30 p-3 rounded-xl text-center">
                  غير متوفر
                </p>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
