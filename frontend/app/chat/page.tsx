"use client";

import { useEffect, useRef, useState } from "react";
import ChatHeader from "@/components/chat/ChatHeader";
import MessageBubble from "@/components/chat/MessageBubble";
import TypingDots from "@/components/chat/TypingDots";
import ChatInput from "@/components/chat/ChatInput";
import { apiGet } from "@/lib/api";

export interface ChatMessage {
  id: string;
  role: "customer" | "user" | "assistant";
  content: string;
  timestamp?: string;
  hasUnitCards?: boolean;
}

// REPLACE when conversation.json exists (Member 4 mock file)
const SAMPLE_CONVERSATION: ChatMessage[] = [
  {
    id: "msg_1",
    role: "assistant",
    content:
      "أهلاً بحضرتك في AqarAI! أنا مساعدك العقاري الذكي. بتدور على شقة أو وحدة في منطقة معينة في مصر؟",
    timestamp: "10:00 ص",
  },
  {
    id: "msg_2",
    role: "customer",
    content:
      "أهلاً، أنا بدور على شقة في New Cairo بمقدم حوالي 250,000 وقسط شهري ميزيدش عن 30,000 جنيه.",
    timestamp: "10:01 ص",
  },
  {
    id: "msg_3",
    role: "assistant",
    content:
      "تمام جداً! ميزانية كويسة ومناسبة لمقدم 250,000 وقسط شهري 30,000 في منطقة New Cairo. بتفضل الاستلام فوري ولا متاح قدامك من سنة لسنتين؟",
    timestamp: "10:02 ص",
  },
  {
    id: "msg_4",
    role: "assistant",
    content:
      "لقيتلك اختيارات ممتازة في New Cairo بتطابق خطتك المالية بالمللي، ودي أول وحدة مرشحة ليك بالتفاصيل والأقساط:",
    timestamp: "10:02 ص",
    hasUnitCards: true,
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(SAMPLE_CONVERSATION);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages from apiGet or fallback to SAMPLE_CONVERSATION
  useEffect(() => {
    async function loadConversation() {
      try {
        const data = await apiGet<ChatMessage[] | { messages: ChatMessage[] }>(
          "/conversations/demo",
          "conversation"
        );
        if (data) {
          const loaded = Array.isArray(data) ? data : data.messages;
          if (loaded && loaded.length > 0) {
            setMessages(loaded);
          }
        }
      } catch {
        // Keep SAMPLE_CONVERSATION on error or missing mock
      }
    }
    loadConversation();
  }, []);

  // Auto-scroll to bottom on new messages or typing state change
  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({
      behavior: smooth ? "smooth" : "auto",
    });
  };

  useEffect(() => {
    scrollToBottom(true);
  }, [messages, isTyping]);

  const handleSendMessage = (text: string) => {
    const now = new Date();
    const timeString = now.toLocaleTimeString("ar-EG", {
      hour: "2-digit",
      minute: "2-digit",
    });

    const newCustomerMsg: ChatMessage = {
      id: `msg_cust_${Date.now()}`,
      role: "customer",
      content: text,
      timestamp: timeString,
    };

    setMessages((prev) => [...prev, newCustomerMsg]);
    setIsTyping(true);

    // Simulate assistant reply after 1 second
    setTimeout(() => {
      setIsTyping(false);
      const newAssistantMsg: ChatMessage = {
        id: `msg_asst_${Date.now()}`,
        role: "assistant",
        content:
          "تمام، فهمت طلبك وبراجعلك باقي الخيارات المتاحة المتوافقة مع الميزانية في New Cairo...",
        timestamp: new Date().toLocaleTimeString("ar-EG", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages((prev) => [...prev, newAssistantMsg]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-sand flex flex-col justify-between">
      {/* Top chat header */}
      <ChatHeader />

      {/* Messages scroll area */}
      <main
        className="flex-1 w-full max-w-3xl mx-auto px-4 py-6 sm:px-6 flex flex-col gap-4 overflow-y-auto"
        aria-live="polite"
      >
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
            hasUnitCards={msg.hasUnitCards}
          />
        ))}

        {/* Typing indicator loop while waiting */}
        {isTyping && <TypingDots />}

        {/* Anchor to ensure keyboard & input don't cover latest message */}
        <div ref={messagesEndRef} className="h-6 shrink-0" />
      </main>

      {/* Fixed bottom input bar */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
    </div>
  );
}
