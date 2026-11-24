export default function TypingDots() {
  return (
    <div
      className="self-end flex items-center gap-1.5 bg-ink text-paper px-4 py-3 rounded-2xl shadow-sm max-w-[80px]"
      role="status"
      aria-label="المساعد يكتب الآن..."
    >
      <span className="w-2 h-2 rounded-full bg-paper animate-typing-1" />
      <span className="w-2 h-2 rounded-full bg-paper animate-typing-2" />
      <span className="w-2 h-2 rounded-full bg-paper animate-typing-3" />
      <span className="sr-only">المساعد يكتب الآن...</span>
    </div>
  );
}
