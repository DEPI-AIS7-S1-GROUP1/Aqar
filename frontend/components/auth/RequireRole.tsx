"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { homeFor, useSession } from "@/lib/auth";
import type { Role } from "@/lib/types";

/** Shows children only to the given role. Others go to /login or to their own home. */
export default function RequireRole({ role, children }: { role: Role; children: ReactNode }) {
  const session = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session.status === "anon") {
      const here = window.location.pathname + window.location.search;
      router.replace(`/login?next=${encodeURIComponent(here)}`);
    } else if (session.status === "authed" && session.user.role !== role) {
      router.replace(homeFor(session.user.role, false));
    }
  }, [session, role, router]);

  if (session.status !== "authed" || session.user.role !== role) {
    return (
      <div className="min-h-[100svh] bg-sand flex items-center justify-center" role="status" aria-label="جاري التحميل">
        <div className="w-10 h-10 rounded-full border-4 border-line border-t-accent animate-spin" />
      </div>
    );
  }
  return <>{children}</>;
}
