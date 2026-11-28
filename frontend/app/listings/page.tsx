import { Suspense } from "react";
import ListingsClient from "./ListingsClient";

export default function ListingsPage() {
  return (
    <Suspense fallback={<div className="min-h-[100svh] bg-paper" />}>
      <ListingsClient />
    </Suspense>
  );
}
