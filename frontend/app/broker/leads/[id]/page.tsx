import { Suspense } from "react";
import RequireRole from "@/components/auth/RequireRole";
import LeadDetailClient from "./LeadDetailClient";

export default function LeadDetailPage() {
  return (
    <RequireRole role="broker">
      <Suspense fallback={<div className="min-h-[100svh] bg-sand" />}>
        <LeadDetailClient />
      </Suspense>
    </RequireRole>
  );
}
