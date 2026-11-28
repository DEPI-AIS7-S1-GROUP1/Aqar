import { Suspense } from "react";
import RequireRole from "@/components/auth/RequireRole";
import ChatClient from "./ChatClient";

export default function ChatPage() {
  return (
    <RequireRole role="customer">
      <Suspense fallback={<div className="min-h-[100svh] bg-sand" />}>
        <ChatClient />
      </Suspense>
    </RequireRole>
  );
}
