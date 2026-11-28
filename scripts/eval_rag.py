"""S2-M1-10: retrieval quality. For each question in eval/rag_questions.json, is the expected
guide among the top 4 hits? Prints hit@4 and the misses.

    python scripts/eval_rag.py              # uses get_rag() (USE_REAL_RAG=1 for pgvector+Gemini)
    python scripts/eval_rag.py --offline    # in-memory index + hash embedder, no key, no DB
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.rag.embeddings import HashEmbedder
from app.rag.search import Rag, build_memory_index, get_rag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=str(ROOT / "eval" / "rag_questions.json"))
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--drafts", action="store_true", help="index draft guides too")
    args = ap.parse_args()

    if args.offline:
        emb = HashEmbedder()
        rag = Rag(build_memory_index(embedder=emb, include_drafts=args.drafts), emb)
    else:
        rag = get_rag()

    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    hits = 0
    for q in questions:
        got = [h.doc_id for h in rag.search(q["question"], k=args.k)]
        ok = q["expected_doc_id"] in got
        hits += ok
        if not ok:
            print(f"MISS  {q['question']}\n      expected {q['expected_doc_id']}, got {got}")
    total = len(questions)
    print(f"hit@{args.k}: {hits}/{total} = {hits / total:.0%}" if total else "no questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
