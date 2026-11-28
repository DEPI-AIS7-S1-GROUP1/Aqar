"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import AuthShell, { Field, SubmitButton } from "@/components/auth/AuthShell";
import { NileLayer, PyramidsLayer, SkyLayer, TowersLayer } from "@/components/scenes/CairoScene";
import { api, ApiError } from "@/lib/api";
import { homeFor, setSession, useSession } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErr, setFieldErr] = useState<Record<string, string>>({});
  const [consent, setConsent] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const name = String(f.get("name") ?? "").trim();
    const email = String(f.get("email") ?? "").trim();
    const password = String(f.get("password") ?? "");
    const phone = String(f.get("phone") ?? "").trim();
    const errs: Record<string, string> = {};
    if (!name) errs.name = "اكتب اسمك.";
    if (!email.includes("@")) errs.email = "اكتب إيميل صحيح.";
    if (password.length < 8) errs.password = "كلمة السر لازم 8 حروف على الأقل.";
    if (phone && !consent) errs.phone = "علّم على الموافقة لو عايز وسيط يكلمك على الرقم ده.";
    setFieldErr(errs);
    setError(null);
    if (Object.keys(errs).length) return;

    setBusy(true);
    try {
      const res = await api.signup({ name, email, password, phone: phone || null, contact_consent: consent });
      setSession(res);
      router.replace(homeFor(res.user.role, res.is_new));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "حصلت مشكلة. جرّب تاني.");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="أهلاً بيك في عقار"
      subtitle="حساب واحد، والمساعد يبدأ معاك على طول. بعد التسجيل هتدخل الشات مباشرة."
      caption="من الأهرامات للبرج الأيقوني، دوّر على اللي يناسبك."
      scene={
        <div className="absolute inset-0">
          <SkyLayer />
          <div className="absolute inset-0"><PyramidsLayer /></div>
          <div className="absolute inset-0"><TowersLayer /></div>
          <div className="absolute inset-0"><NileLayer /></div>
        </div>
      }
    >
      {session.status === "authed" ? (
        <div className="rounded-2xl border border-paper/15 p-5">
          <p>أنت داخل بالفعل باسم {session.user.name}.</p>
          <Link href={homeFor(session.user.role, session.isNew)} className="mt-4 inline-block bg-paper text-ink px-5 py-2.5 rounded-full font-bold">
            كمّل
          </Link>
        </div>
      ) : (
        <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
          <Field label="الاسم" id="name" name="name" autoComplete="name" placeholder="اسمك" error={fieldErr.name} />
          <Field label="الإيميل" id="email" name="email" type="email" dir="ltr" autoComplete="email" placeholder="you@example.com" error={fieldErr.email} />
          <Field label="كلمة السر" id="password" name="password" type="password" dir="ltr" autoComplete="new-password" hint="8 حروف على الأقل" error={fieldErr.password} />
          <Field label="رقم الموبايل (اختياري)" id="phone" name="phone" type="tel" dir="ltr" autoComplete="tel" placeholder="01xxxxxxxxx" hint="بيتشاف بس للوسيط لما تطلب تواصل، ومش بيتبعت للمساعد." error={fieldErr.phone} />
          <label className="flex items-start gap-3 text-sm text-muted-dark cursor-pointer select-none">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-1 w-5 h-5 accent-[#C8372F]"
            />
            موافق إن وسيط من الفريق يتواصل معايا.
          </label>
          {error && (
            <p role="alert" className="rounded-2xl bg-accent/15 border border-accent/40 px-4 py-3 text-sm">
              {error}
            </p>
          )}
          <SubmitButton busy={busy}>إنشاء الحساب</SubmitButton>
          <p className="text-center text-sm text-muted-dark">
            عندك حساب؟{" "}
            <Link href="/login" className="text-paper font-bold hover:underline underline-offset-4">
              سجل دخول
            </Link>
          </p>
        </form>
      )}
    </AuthShell>
  );
}
