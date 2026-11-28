"""Read the knowledge guides in data/docs/ and split them into chunks.

Each guide is a Markdown file with front matter:

    ---
    doc_type: area_guide            # or developer_profile
    entity_id: sheikh_zayed         # canonical area key or developer slug
    title: الشيخ زايد (Sheikh Zayed)
    lang: ar
    status: ready                   # draft files are skipped by the ingest
    sources:
      - https://official-page.example
    ---
    ## نظرة عامة
    Text ... [المصدر](https://link-for-this-fact)

One ``##`` section = one chunk (long sections are split by paragraph). Every chunk needs a
source: the first link inside the section, otherwise the first URL in ``sources``. A chunk
with no source at all is an error, so nothing unsourced can reach a customer.
Pure code: no network, no database.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.rag.models import Chunk

MAX_CHARS = 1400  # about 300-400 tokens of Arabic text
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BARE_URL_RE = re.compile(r"https?://[^\s)>\]]+")
GENERIC_LINK_TEXT = {"المصدر", "مصدر", "source", "link", "رابط", "هنا", "here"}
REQUIRED_KEYS = ("doc_type", "entity_id", "title")


class DocError(ValueError):
    pass


@dataclass
class Doc:
    path: Path
    doc_id: str
    doc_type: str
    entity_id: str
    title: str
    lang: str
    status: str
    sources: list[str]
    body: str
    meta: dict[str, str] = field(default_factory=dict)


def parse_front_matter(raw: str) -> tuple[dict[str, object], str]:
    """Tiny YAML subset: ``key: value`` lines and ``key:`` followed by ``  - item`` lines."""
    text = raw.lstrip("﻿")
    if not text.startswith("---"):
        raise DocError("missing front matter (file must start with ---)")
    end = text.find("\n---", 3)
    if end == -1:
        raise DocError("front matter is not closed with ---")
    header = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, object] = {}
    current_list: list[str] | None = None
    for line in header.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s*-\s+(.*)$", line)
        if item and current_list is not None:
            current_list.append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not kv:
            raise DocError(f"cannot read front matter line: {line!r}")
        key, value = kv.group(1), kv.group(2).strip()
        if value == "":
            current_list = []
            meta[key] = current_list
        else:
            current_list = None
            meta[key] = value.strip("'\"")
    return meta, body


def load_doc(path: Path, root: Path) -> Doc:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    for key in REQUIRED_KEYS:
        if not meta.get(key):
            raise DocError(f"{path.name}: front matter needs {key}")
    doc_type = str(meta["doc_type"])
    if doc_type not in ("area_guide", "developer_profile"):
        raise DocError(f"{path.name}: doc_type must be area_guide or developer_profile")
    sources = meta.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    return Doc(
        path=path,
        doc_id=path.relative_to(root).with_suffix("").as_posix(),
        doc_type=doc_type,
        entity_id=str(meta["entity_id"]),
        title=str(meta["title"]),
        lang=str(meta.get("lang") or "ar"),
        status=str(meta.get("status") or "draft"),
        sources=[s for s in sources if s.startswith("http")],
        body=body,
        meta={k: v for k, v in meta.items() if isinstance(v, str)},
    )


def load_docs(root: Path, *, include_drafts: bool = False) -> tuple[list[Doc], list[str]]:
    """All guides under ``root``. Returns (docs, problems). Drafts are skipped by default."""
    docs: list[Doc] = []
    problems: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() == "readme.md" or path.name.startswith("_"):
            continue
        try:
            doc = load_doc(path, root)
        except DocError as e:
            problems.append(str(e))
            continue
        if doc.status != "ready" and not include_drafts:
            problems.append(f"{doc.doc_id}: skipped (status: {doc.status})")
            continue
        docs.append(doc)
    return docs, problems


def _sections(body: str) -> list[tuple[str, str]]:
    """(heading, text) per ``##`` section. Text before the first heading gets heading ''."""
    parts: list[tuple[str, str]] = []
    heading = ""
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            if "\n".join(buf).strip():
                parts.append((heading, "\n".join(buf).strip()))
            heading, buf = m.group(1).strip(), []
        elif not line.startswith("# "):  # the H1 repeats the title
            buf.append(line)
    if "\n".join(buf).strip():
        parts.append((heading, "\n".join(buf).strip()))
    return parts


def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    cur = ""
    for para in re.split(r"\n\s*\n", text):
        if cur and len(cur) + len(para) + 2 > max_chars:
            pieces.append(cur.strip())
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        pieces.append(cur.strip())
    return pieces


def _source_for(text: str, doc: Doc) -> tuple[str, str]:
    link = LINK_RE.search(text)
    if link:
        label = link.group(1).strip()
        return link.group(2), (doc.title if label.lower() in GENERIC_LINK_TEXT else label)
    bare = BARE_URL_RE.search(text)
    if bare:
        return bare.group(0), doc.title
    if doc.sources:
        return doc.sources[0], doc.title
    raise DocError(f"{doc.doc_id}: a section has no source link and the doc has no sources")


def chunk_doc(doc: Doc, *, max_chars: int = MAX_CHARS) -> list[Chunk]:
    if doc.status == "ready" and ("TODO" in doc.body or "https://..." in doc.body):
        raise DocError(f"{doc.doc_id}: status is ready but the text still has TODO or a placeholder link")
    chunks: list[Chunk] = []
    for heading, text in _sections(doc.body):
        for piece in _split_long(text, max_chars):
            url, label = _source_for(piece, doc)
            idx = len(chunks)
            digest = hashlib.sha256(
                f"{doc.title}\n{heading}\n{piece}\n{url}".encode()
            ).hexdigest()
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}#{idx}",
                    doc_id=doc.doc_id,
                    doc_type=doc.doc_type,  # type: ignore[arg-type]
                    entity_id=doc.entity_id,
                    lang=doc.lang,
                    title=doc.title,
                    heading=heading,
                    text=piece,
                    source_url=url,
                    source_title=label,
                    content_hash=digest,
                )
            )
    if not chunks:
        raise DocError(f"{doc.doc_id}: no text to index")
    return chunks
