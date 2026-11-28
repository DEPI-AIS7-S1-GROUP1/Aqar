"""S2-M1-10: load the guides in data/docs/ into the rag_chunks table.

Usage (from the repo root, with DATABASE_URL and GEMINI_API_KEY in your environment):

    python scripts/ingest_docs.py              # ingest ready guides into Postgres
    python scripts/ingest_docs.py --check      # only read + chunk, no key, no database
    python scripts/ingest_docs.py --drafts     # include status: draft files (testing only)

Idempotent: unchanged chunks are not re-embedded (saves free-tier quota), changed chunks are
re-embedded, and chunks of deleted sections or files are removed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.rag.docs import DocError, chunk_doc, load_docs
from app.rag.embeddings import GeminiEmbedder, HashEmbedder
from app.rag.store import PgVectorStore


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docs", default=str(ROOT / "data" / "docs"))
    ap.add_argument("--check", action="store_true", help="read and chunk only")
    ap.add_argument("--drafts", action="store_true", help="also ingest status: draft files")
    ap.add_argument("--offline", action="store_true", help="use the offline hash embedder")
    args = ap.parse_args()

    root = Path(args.docs)
    docs, problems = load_docs(root, include_drafts=args.drafts)
    chunks = []
    for d in docs:
        try:
            chunks.extend(chunk_doc(d))
        except DocError as e:
            problems.append(str(e))

    by_type: dict[str, int] = {}
    for d in docs:
        by_type[d.doc_type] = by_type.get(d.doc_type, 0) + 1
    print(f"guides: {len(docs)} {by_type}  chunks: {len(chunks)}")
    for p in problems:
        print(f"  note: {p}")
    if args.check:
        for c in chunks:
            print(f"  {c.chunk_id:45} {len(c.text):5} chars  source: {c.source_url}")
        return 1 if any("skipped" not in p for p in problems) else 0
    if not chunks:
        print("nothing to ingest (are the guides still status: draft?)")
        return 1

    embedder = HashEmbedder() if args.offline else GeminiEmbedder()
    store = PgVectorStore()
    old = store.existing_hashes()
    todo = [c for c in chunks if old.get(c.chunk_id) != c.content_hash]
    print(f"embedding {len(todo)} new/changed chunks with {embedder.name} "
          f"({len(chunks) - len(todo)} unchanged)")
    if todo:
        vectors = embedder.embed([c.embed_input() for c in todo])
        for c, v in zip(todo, vectors, strict=True):
            c.embedding = v
        store.upsert(todo, embedder.name)
    removed = store.delete_except(c.chunk_id for c in chunks)
    print(f"done: upserted {len(todo)}, removed {removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
