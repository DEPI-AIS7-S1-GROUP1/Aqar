"""Where chunks and their vectors live.

* ``PgVectorStore``: the ``rag_chunks`` table (migration 0005) in Postgres with pgvector.
  Cosine distance ``<=>``; score = 1 - distance. No extra Python package: vectors are sent as
  text and cast with ``::vector``.
* ``InMemoryStore``: same API in a Python list, for tests and for running without a database.
"""

from __future__ import annotations

import math
import os
from collections.abc import Iterable, Sequence
from typing import Protocol

from app.rag.models import Chunk, RagHit


class VectorStore(Protocol):
    def existing_hashes(self) -> dict[str, str]: ...
    def upsert(self, chunks: Sequence[Chunk], embedder_name: str) -> int: ...
    def delete_except(self, keep_chunk_ids: Iterable[str]) -> int: ...
    def search(
        self,
        vector: Sequence[float],
        k: int,
        entity_id: str | None = None,
        doc_type: str | None = None,
    ) -> list[RagHit]: ...


def _hit(c: Chunk, score: float) -> RagHit:
    return RagHit(
        text=c.text,
        doc_id=c.doc_id,
        source_url=c.source_url,
        score=score,
        doc_type=c.doc_type,
        entity_id=c.entity_id,
        title=c.title,
        heading=c.heading or None,
        source_title=c.source_title,
    )


class InMemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, Chunk] = {}

    def existing_hashes(self) -> dict[str, str]:
        return {cid: c.content_hash for cid, c in self.rows.items()}

    def upsert(self, chunks: Sequence[Chunk], embedder_name: str) -> int:
        for c in chunks:
            if c.embedding is None:
                raise ValueError(f"{c.chunk_id} has no embedding")
            self.rows[c.chunk_id] = c
        return len(chunks)

    def delete_except(self, keep_chunk_ids: Iterable[str]) -> int:
        keep = set(keep_chunk_ids)
        gone = [cid for cid in self.rows if cid not in keep]
        for cid in gone:
            del self.rows[cid]
        return len(gone)

    def search(self, vector, k, entity_id=None, doc_type=None) -> list[RagHit]:
        scored = []
        for c in self.rows.values():
            if entity_id and c.entity_id != entity_id:
                continue
            if doc_type and c.doc_type != doc_type:
                continue
            dot = sum(a * b for a, b in zip(vector, c.embedding or [], strict=False))
            na = math.sqrt(sum(a * a for a in vector)) or 1.0
            nb = math.sqrt(sum(b * b for b in c.embedding or [])) or 1.0
            scored.append((dot / (na * nb), c))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [_hit(c, s) for s, c in scored[:k]]


def _vec_literal(v: Sequence[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


def _plain_url(url: str) -> str:
    """psycopg wants postgresql://; Alembic-style URLs may carry +psycopg."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url.replace("postgresql+psycopg://", "postgresql://")


class PgVectorStore:
    def __init__(self, database_url: str | None = None):
        url = database_url or os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL is not set")
        self.url = _plain_url(url)

    def _connect(self):
        import psycopg  # lazy: unit tests run without a database driver

        return psycopg.connect(self.url, autocommit=True)

    def existing_hashes(self) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT chunk_id, content_hash FROM rag_chunks").fetchall()
        return {r[0]: r[1] for r in rows}

    def upsert(self, chunks: Sequence[Chunk], embedder_name: str) -> int:
        sql = """
        INSERT INTO rag_chunks (chunk_id, doc_id, doc_type, entity_id, lang, title, heading,
                                text, source_url, source_title, content_hash, embedder,
                                embedding, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, now())
        ON CONFLICT (chunk_id) DO UPDATE SET
            doc_id = EXCLUDED.doc_id, doc_type = EXCLUDED.doc_type,
            entity_id = EXCLUDED.entity_id, lang = EXCLUDED.lang, title = EXCLUDED.title,
            heading = EXCLUDED.heading, text = EXCLUDED.text,
            source_url = EXCLUDED.source_url, source_title = EXCLUDED.source_title,
            content_hash = EXCLUDED.content_hash, embedder = EXCLUDED.embedder,
            embedding = EXCLUDED.embedding, updated_at = now()
        """
        with self._connect() as conn, conn.transaction():
            for c in chunks:
                if c.embedding is None:
                    raise ValueError(f"{c.chunk_id} has no embedding")
                conn.execute(
                    sql,
                    (
                        c.chunk_id, c.doc_id, c.doc_type, c.entity_id, c.lang, c.title,
                        c.heading, c.text, c.source_url, c.source_title, c.content_hash,
                        embedder_name, _vec_literal(c.embedding),
                    ),
                )
        return len(chunks)

    def delete_except(self, keep_chunk_ids: Iterable[str]) -> int:
        keep = list(keep_chunk_ids)
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM rag_chunks WHERE NOT (chunk_id = ANY(%s))", (keep,)
            )
            return cur.rowcount or 0

    def search(self, vector, k, entity_id=None, doc_type=None) -> list[RagHit]:
        v = _vec_literal(vector)
        sql = """
        SELECT chunk_id, doc_id, doc_type, entity_id, lang, title, heading, text,
               source_url, source_title, content_hash,
               1 - (embedding <=> %s::vector) AS score
        FROM rag_chunks
        WHERE (%s::text IS NULL OR entity_id = %s)
          AND (%s::text IS NULL OR doc_type = %s)
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        with self._connect() as conn:
            rows = conn.execute(
                sql, (v, entity_id, entity_id, doc_type, doc_type, v, k)
            ).fetchall()
        hits = []
        for r in rows:
            c = Chunk(
                chunk_id=r[0], doc_id=r[1], doc_type=r[2], entity_id=r[3], lang=r[4],
                title=r[5], heading=r[6], text=r[7], source_url=r[8], source_title=r[9],
                content_hash=r[10],
            )
            hits.append(_hit(c, float(r[11])))
        return hits
