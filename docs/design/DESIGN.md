# AqarAI design spec (for Antigravity)

Source of truth for how every screen looks. Live mockup: https://claude.ai/artifact/59DcQbh3uWnifjVmVSXQW9
Stack: Next.js (App Router) + TypeScript + Tailwind. Arabic first, right-to-left (RTL).

## 1. Look in one line
Dark ink + warm white + one red accent. Big Arabic type, curved lines, calm motion. Marketing page is dramatic; the product screens (chat, broker) stay quiet and fast.

## 2. Tokens (put in tailwind config / globals.css as CSS variables, use ONLY these)
| Name | Hex | Use |
|---|---|---|
| ink | #0E1116 | dark background, main text |
| paper | #F4F1EA | page background on product screens, text on dark |
| sand | #EDE9DF | chat background, dividers |
| line | #CFCAB9 | borders, inputs |
| muted | #4A4A45 | secondary text on light |
| muted-dark | #B9B6AE | secondary text on dark |
| accent | #C8372F | buttons, Hot, highlights (white text passes 4.5:1) |
| hot | #C8372F | Hot badge (white text) |
| warm | #B45309 | Warm badge (white text) |
| cold | #2F5D8C | Cold badge (white text) |

Affordability badges (always colour + text label, never colour alone):
| Status (code value) | Arabic label | Background | Text |
|---|---|---|---|
| fit | مناسبة | #DDF1E4 | #14532D |
| tight | ضاغطة | #FCEBC8 | #7A4B00 |
| not_fit | مش مناسبة | #FBDADA | #7F1D1D |
| unknown | غير معروف | #E4E1D8 | #3F3F3A |

Mode badge (LeadState.mode): AI_ACTIVE = "الـ AI شغال", HANDOFF_PENDING = "في انتظار الموظف", HUMAN_ACTIVE = "الموظف مستلم", CLOSED = "مقفولة". Grey pill (#E4E1D8 on #3F3F3A) for all.

## 3. Type and layout
- Font: Noto Kufi Arabic (400, 700, 900) via next/font/google. Fallback: system sans-serif.
- html lang="ar" dir="rtl". Every chat bubble uses dir="auto" so Arabic and English words mix correctly.
- Radius: cards 16px, rows 14px, pills 999px. Touch targets at least 44px.
- Spacing: multiples of 4px. Page padding 48px desktop, 16-20px phone.
- Motion: only slow ambient motion on the landing page (ring spin 40s, building drift 7s, scroll circle bob 2.4s) and hover lift (translateY -2px). Wrap ALL animation in @media (prefers-reduced-motion: no-preference). No animation on chat or broker pages except the typing dots.
- Never emoji. Icons are inline SVG stroke icons.

## 4. Screens and files (frontend/app)
### Landing: app/page.tsx  (desktop first, works at 375px)
- Dark ink background. Giant faint word "عقار" behind everything (colour paper at 5% opacity).
- Building drawing: /hero-building.svg (file in frontend/public). Bottom-left, absolute, width 780px (max 62%). To use a real photo later, replace the file and keep the same size.
- Rotating text ring (SVG textPath, ONE path, never split Arabic into single letters): "مساعد مبيعات عقاري ● بالعامية المصرية ●".
- Top bar: logo "AqarAI", links (الرئيسية، إزاي بيشتغل، الوحدات، لوحة الوسيط), pill button "ابدأ المحادثة" (paper bg, ink text; hover accent).
- Headline 64px/900: "يفهم العميل. / يتأكد إنه يقدر يدفع. / يسلّمه للوسيط جاهز." Sub paragraph 18px muted-dark. Buttons: "جرّب المحادثة" (accent) -> /chat, "شوف لوحة الوسيط" (outline) -> /broker.
- Three step chips: التأهيل، البحث والمطابقة، التسليم للموظف.
- Red scroll circle bottom-left. NO invented statistics anywhere.
- Do NOT build a public listings browse/search page. Listings appear only as unit cards in chat and in the broker brief.

### Customer chat: app/chat/page.tsx  (phone first, 375px)
- Header (ink): round accent avatar "A", name "مساعد AqarAI", status "متاح دلوقتي".
- Message area on sand. Customer bubble: white, aligned to the start side. Assistant bubble: ink with paper text, aligned to the end side. Max width 80%.
- Unit card slot inside assistant messages (Member 2 builds components/UnitCard.tsx). Card: white, price bold, one line plan summary, affordability badge, small note "أرقام توضيحية" while data is mock.
- Typing indicator: three dots, 1.2s fade loop, only while waiting.
- Input bar (paper): label for the input (visually hidden), rounded input, round ink send button with aria-label "إرسال". Enter sends. Keep list scrolled to newest message.

### Broker leads list: app/broker/page.tsx  (desktop and phone)
- Top bar ink: logo, tabs "العملاء" (active, accent underline) and "التحليلات".
- Title "العملاء" + line "مرتبين من الأعلى تقييمًا".
- Filter chips: الكل، Hot، Warm، Cold with counts.
- Rows sorted by score, highest first. Row = white card: lead name or id, score number + progress bar (bar colour = band colour), band badge (Hot/Warm/Cold, text label), main interest line, time since last message. Whole row is a link to /broker/leads/[id]. Hover lifts. Under 760px the row becomes two columns. Empty state: short message.
- Band rule: Cold below 40, Warm 40-69, Hot 70 and above.

### Lead brief: app/broker/leads/[id]/page.tsx
- Header: lead id, band badge with score ("Hot · 92"), mode badge, and an empty dashed box reserved for the takeover buttons (built in Sprint 3).
- Two columns (stack under 900px). Main column: Summary (summary_text), Suggested units (matched_units with affordability badge), Open questions. Side column: Confirmed requirements (areas, down payment, monthly capacity, timeline, purpose), Unconfirmed slots, "ليه التقييم" list (score reasons).
- Every field of LeadBrief must appear. A None value shows "غير متوفر". NEVER show 0 for unknown, never leave blank.

## 5. Data
- Types come from backend/app/contracts.py (LeadState, LeadBrief, SlotPatch, AffordabilityEntry). Write matching TypeScript types in frontend/lib/types.ts.
- All data goes through frontend/lib/api.ts. With NEXT_PUBLIC_USE_MOCKS=true it reads frontend/mocks/*.json (conversation.json, leads.json, lead_detail.json). If a mock file is missing, show a clearly marked built-in sample, never crash.
- No personal data in code or mocks: leads are "عميل 1042" style ids.
- Sample numbers (illustrative only): unit 3,000,000 EGP, down payment 5% = 150,000, instalment 29,688 x 8 years. These must later come from the calculator, never typed in UI code.

## 6. Do not
- Do not add other colours, fonts or libraries (no UI kit, no animation library) without asking.
- Do not split Arabic text into letters. Do not use px widths that break at 375px.
- Do not use localStorage for app data.
