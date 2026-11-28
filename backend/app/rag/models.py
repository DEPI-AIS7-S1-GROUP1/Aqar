"""Data shapes for RAG.

``RagHit`` is the shape in the Sprint 2 contract pack (Appendix A) plus a few optional display
fields (title, heading, source_title) used for the source chips in the chat. When contracts-v2
lands, RagHit moves to app/contracts.py unchanged and this module re-exports it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DocType = Literal["area_guide", "developer_profile"]


class RagHit(BaseModel):
    text: str
    doc_id: str
    source_url: str
    score: float
    # display extras (optional, not needed by the agent)
    doc_type: DocType | None = None
    entity_id: str | None = None
    title: str | None = None
    heading: str | None = None
    source_title: str | None = None


class Chunk(BaseModel):
    """One searchable piece of a guide: one section (or part of a long section)."""

    chunk_id: str
    doc_id: str
    doc_type: DocType
    entity_id: str
    lang: str
    title: str
    heading: str
    text: str
    source_url: str
    source_title: str
    content_hash: str
    embedding: list[float] | None = Field(default=None, repr=False)

    def embed_input(self) -> str:
        """What gets embedded: title + heading give the chunk its context."""
        return f"{self.title}\n{self.heading}\n{self.text}"
