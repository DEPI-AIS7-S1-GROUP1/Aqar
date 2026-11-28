# Knowledge guides for the assistant (RAG)

The assistant answers questions about **areas** and **developers** only from these files, and
shows the source of every answer as a chip in the chat. If a fact is not here, it says it does
not know and offers a broker. So: what is written here is what customers will read.

```
data/docs/
  areas/<area_key>.md          one guide per area (keys: new_cairo, sheikh_zayed, october_6,
                               new_capital, mostakbal_city, maadi)
  developers/<developer>.md    one profile per developer (sodic, palm_hills, hyde_park, ...)
```

## How to write one guide

1. Open the template and fill every `TODO:` line. Arabic, short, neutral. About 250 to 400 words
   per file.
2. **Every fact needs a source right after it**: `... [موقع المطور](https://...)`. The chip in the
   chat shows the first link of each section, so put the strongest source first.
3. Put the main official links in `sources:` at the top too.
4. When done, change `status: draft` to `status: ready`. Files still containing `TODO` are
   refused, and drafts are never loaded.
5. Check it: `python scripts/ingest_docs.py --check` (no key, no database needed).

## Good sources
Developer official websites and press releases, the Egyptian Exchange (for listed developers),
government pages (NUCA, ministries), reputable Egyptian business news.

## Rules
- **No unsourced claims**, positive or negative. Never write that a developer is late or
  unreliable without a reputable source; if there is none, leave it out.
- **No prices or payment numbers here.** Numbers come from the calculator and the listings data,
  never from these texts, so they cannot contradict each other.
- **No personal data**: no phone numbers, no names of sales agents or customers.
- Do not copy whole paragraphs from a website: summarise in your own words and link the source.

## Run (on your laptop)
```
cd infra && docker compose up -d db              # Postgres with pgvector
cd ../backend && alembic upgrade head            # creates rag_chunks (migration 0005)
cd .. && python scripts/ingest_docs.py           # needs GEMINI_API_KEY and DATABASE_URL in .env
python scripts/eval_rag.py                       # hit@4 on eval/rag_questions.json (USE_REAL_RAG=1)
```
