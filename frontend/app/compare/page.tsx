import { Suspense } from "react";
import CompareClient from "./CompareClient";

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="min-h-[100svh] bg-paper" />}>
      <CompareClient />
    </Suspense>
  );
}
