"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import AuthShell, { Field, SubmitButton } from "@/components/auth/AuthShell";
import { AlexandriaNight } from "@/components/scenes/MiniScenes";
import { api, ApiError, USE_MOCKS } from "@/lib/api";
import { homeFor, setSession, useSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const email = String(f.get("email") ?? "").trim();
    const password = String(f.get("password") ?? "");
    if (!email || !password) {
      setError("اكتب الإيميل وكلمة السر.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await api.login({ email, password });
      setSession(res);
      const next = new URLSearchParams(window.location.search).get("next");
      const safeNext = next && next.startsWith("/") && !next.startsWith("//") ? next : null;
      const okForRole = safeNext && (res.user.role === "broker") === safeNext.startsWith("/broker");
      router.replace(okForRole ? safeNext! : homeFor(res.user.role, res.is_new));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "حصلت مشكلة. جرّب تاني.");
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="نورتنا تاني"
      subtitle="ادخل بحسابك. العملاء بيروحوا للمساعد، والوسطاء بيروحوا للوحة العملاء على طول."
      caption="من قلعة قايتباي لكورنيش إسكندرية، بيتك مستنيك."
      scene={<AlexandriaNight />}
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
          <Field label="الإيميل" id="email" name="email" type="email" dir="ltr" autoComplete="email" placeholder="you@example.com" />
          <Field label="كلمة السر" id="password" name="password" type="password" dir="ltr" autoComplete="current-password" />
          {error && (
            <p role="alert" className="rounded-2xl bg-accent/15 border border-accent/40 px-4 py-3 text-sm">
              {error}
            </p>
          )}
          <SubmitButton busy={busy}>تسجيل الدخول</SubmitButton>
          <p className="text-center text-sm text-muted-dark">
            لسه معندكش حساب؟{" "}
            <Link href="/signup" className="text-paper font-bold hover:underline underline-offset-4">
              اعمل حساب
            </Link>
          </p>
          {USE_MOCKS && (
            <div className="mt-2 rounded-2xl border border-dashed border-paper/20 p-4 text-xs text-muted-dark leading-relaxed">
              <p className="font-bold text-paper/90 mb-1">وضع العرض التجريبي</p>
              وسيط: <span dir="ltr">broker@aqar.demo / broker123</span>
              <br />
              عميل: <span dir="ltr">demo@aqar.demo / demo1234</span>
              <br />
              أي إيميل جديد بيتعمله حساب، ولو فيه كلمة broker بيدخل كوسيط.
            </div>
          )}
        </form>
      )}
    </AuthShell>
  );
}
