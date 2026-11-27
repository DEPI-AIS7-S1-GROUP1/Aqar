"""The Rag service: ``search(query, k, entity_id)`` -> list[RagHit].

This is the ``Rag`` interface from the Sprint 2 contract pack (Appendix C). Member 4's
``answer`` node calls it through the registry; the conversation API never calls it directly.

``get_rag()`` picks the implementation:
* USE_REAL_RAG=1 -> pgvector (DATABASE_URL) + Gemini (GEMINI_API_KEY). Run ingest_docs first.
* otherwise      -> in-memory index built from data/docs with the offline HashEmbedder.
  Same answers shape, no key and no database needed (dev, tests, demo fallback).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from app.rag.docs import chunk_doc, load_docs
from app.rag.embeddings import Embedder, GeminiEmbedder, HashEmbedder
from app.rag.models import RagHit
from app.rag.store import InMemoryStore, PgVectorStore, VectorStore

DOCS_ROOT = Path(
    os.getenv("RAG_DOCS_DIR") or Path(__file__).resolve().parents[3] / "data" / "docs"
)


class Rag:
    def __init__(self, store: VectorStore, embedder: Embedder, *, min_score: float = 0.0):
        self.store = store
        self.embedder = embedder
        self.min_score = min_score

    def search(
        self,
        query: str,
        k: int = 4,
        entity_id: str | None = None,
        doc_type: str | None = None,
    ) -> list[RagHit]:
        """Top-``k`` chunks for ``query``. ``entity_id`` limits to one area/developer.

        Hits under ``min_score`` are dropped, so "nothing relevant" comes back as an empty
        list and the agent can say it does not know instead of guessing.
        """
        q = (query or "").strip()
        if not q:
            return []
        vector = self.embedder.embed([q])[0]
        hits = self.store.search(vector, max(1, k), entity_id=entity_id, doc_type=doc_type)
        return [h for h in hits if h.score >= self.min_score]


def build_memory_index(root: Path = DOCS_ROOT, embedder: Embedder | None = None,
                       *, include_drafts: bool = False) -> InMemoryStore:
    embedder = embedder or HashEmbedder()
    docs, _ = load_docs(root, include_drafts=include_drafts)
    chunks = [c for d in docs for c in chunk_doc(d)]
    vectors = embedder.embed([c.embed_input() for c in chunks]) if chunks else []
    for c, v in zip(chunks, vectors, strict=True):
        c.embedding = v
    store = InMemoryStore()
    store.upsert(chunks, embedder.name)
    return store


@lru_cache(maxsize=1)
def get_rag() -> Rag:
    min_score = float(os.getenv("RAG_MIN_SCORE", "0.0"))
    if os.getenv("USE_REAL_RAG") == "1":
        return Rag(PgVectorStore(), GeminiEmbedder(), min_score=min_score)
    embedder = HashEmbedder()
    return Rag(build_memory_index(DOCS_ROOT, embedder), embedder, min_score=min_score)
