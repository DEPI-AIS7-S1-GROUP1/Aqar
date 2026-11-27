"""S2-M1-10 RAG chunks table (pgvector).

One row per searchable piece of a guide (area guide or developer profile). Every row has a
source_url, so every answer can show where it came from. The vector size (768) matches
EMBED_DIM in app/rag/embeddings.py; changing it means a new migration and a full re-ingest.

Revision ID: 0005
Revises: 0003
"""

from alembic import op

revision = "0005"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE TABLE rag_chunks (
            chunk_id      text PRIMARY KEY,
            doc_id        text NOT NULL,
            doc_type      text NOT NULL
                          CHECK (doc_type IN ('area_guide', 'developer_profile')),
            entity_id     text NOT NULL,
            lang          text NOT NULL DEFAULT 'ar',
            title         text NOT NULL,
            heading       text NOT NULL DEFAULT '',
            text          text NOT NULL CHECK (length(text) > 0),
            source_url    text NOT NULL CHECK (source_url ~ '^https?://'),
            source_title  text NOT NULL,
            content_hash  text NOT NULL,
            embedder      text NOT NULL,
            embedding     vector(768) NOT NULL,
            created_at    timestamptz NOT NULL DEFAULT now(),
            updated_at    timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_rag_chunks_entity ON rag_chunks (entity_id)")
    op.execute("CREATE INDEX ix_rag_chunks_doc ON rag_chunks (doc_id)")
    # No ANN index: with a few hundred chunks an exact scan is fast and exact.


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS rag_chunks")
