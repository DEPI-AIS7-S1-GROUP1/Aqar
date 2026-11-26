import { Suspense } from "react";
import UnitDetailClient from "./UnitDetailClient";

export default function UnitDetailPage() {
  return (
    <Suspense fallback={<div className="min-h-[100svh] bg-paper" />}>
      <UnitDetailClient />
    </Suspense>
  );
}
