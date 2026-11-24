"use client";

import { useEffect, useRef, useState } from "react";
import ChatHeader from "@/components/chat/ChatHeader";
import MessageBubble from "@/components/chat/MessageBubble";
import TypingDots from "@/components/chat/TypingDots";
import ChatInput from "@/components/chat/ChatInput";
import { apiGet } from "@/lib/api";
import { ChatMessage } from "@/lib/types";
import { SAMPLE_CONVERSATION } from "@/lib/sample-data";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(SAMPLE_CONVERSATION);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages with apiGet or fallback to SAMPLE_CONVERSATION
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
        // Fallback to SAMPLE_CONVERSATION if mock does not exist
      }
    }
    loadConversation();
  }, []);

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

    // Simulate assistant reply locally after 1 second with no network call
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
      {/* Top chat header on ink */}
      <ChatHeader />

      {/* Messages scroll area on sand */}
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
            unit={msg.unit}
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
