"""S2-M1-10: tests for reading/chunking guides and in-memory search (no key, no database)."""

import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.rag.docs import DocError, chunk_doc, load_docs, parse_front_matter
from app.rag.embeddings import EMBED_DIM, HashEmbedder, normalise
from app.rag.search import Rag, build_memory_index

ZAYED = """---
doc_type: area_guide
entity_id: sheikh_zayed
title: الشيخ زايد
lang: ar
status: ready
sources:
  - https://official.example/zayed
---
# الشيخ زايد

## نظرة عامة
مدينة في غرب القاهرة قريبة من المتحف المصري الكبير وطريق الواحات.
[هيئة المجتمعات العمرانية](https://nuca.example/zayed)

## مناسبة لمين؟
مناسبة للعائلات لأن فيها مدارس دولية كتير ومساحات خضرا.
"""

SODIC = """---
doc_type: developer_profile
entity_id: sodic
title: سوديك
status: ready
sources:
  - https://sodic.example
---
## نبذة عن المطور
شركة تطوير عقاري مصرية مقيدة في البورصة وعندها مشروعات في التجمع وزايد. [المصدر](https://sodic.example/about)
"""

MAADI = """---
doc_type: area_guide
entity_id: maadi
title: المعادي
status: ready
sources:
  - https://maadi.example
---
## نظرة عامة
حي هادي جنوب القاهرة على النيل، فيه كورنيش وأبراج سكنية قديمة وجديدة.
"""

DRAFT = """---
doc_type: area_guide
entity_id: october_6
title: 6 أكتوبر
status: draft
---
## نظرة عامة
TODO: اكتب هنا
"""


@pytest.fixture
def docs_root(tmp_path: Path) -> Path:
    (tmp_path / "areas").mkdir()
    (tmp_path / "developers").mkdir()
    (tmp_path / "areas" / "sheikh_zayed.md").write_text(ZAYED, encoding="utf-8")
    (tmp_path / "areas" / "maadi.md").write_text(MAADI, encoding="utf-8")
    (tmp_path / "areas" / "october_6.md").write_text(DRAFT, encoding="utf-8")
    (tmp_path / "developers" / "sodic.md").write_text(SODIC, encoding="utf-8")
    (tmp_path / "README.md").write_text("# not a guide", encoding="utf-8")
    return tmp_path


def test_front_matter_with_list():
    meta, body = parse_front_matter(ZAYED)
    assert meta["entity_id"] == "sheikh_zayed"
    assert meta["sources"] == ["https://official.example/zayed"]
    assert body.startswith("# الشيخ زايد")


def test_front_matter_required():
    with pytest.raises(DocError):
        parse_front_matter("no front matter here")


def test_drafts_and_readme_are_skipped(docs_root):
    docs, problems = load_docs(docs_root)
    assert sorted(d.doc_id for d in docs) == ["areas/maadi", "areas/sheikh_zayed", "developers/sodic"]
    assert any("october_6" in p and "draft" in p for p in problems)


def test_one_chunk_per_section_with_its_own_source(docs_root):
    docs, _ = load_docs(docs_root)
    zayed = next(d for d in docs if d.entity_id == "sheikh_zayed")
    chunks = chunk_doc(zayed)
    assert [c.heading for c in chunks] == ["نظرة عامة", "مناسبة لمين؟"]
    assert chunks[0].source_url == "https://nuca.example/zayed"
    assert chunks[0].source_title == "هيئة المجتمعات العمرانية"
    # no link in the section -> the doc's first source
    assert chunks[1].source_url == "https://official.example/zayed"
    assert chunks[0].chunk_id == "areas/sheikh_zayed#0"


def test_generic_link_text_uses_doc_title(docs_root):
    docs, _ = load_docs(docs_root)
    (c,) = chunk_doc(next(d for d in docs if d.entity_id == "sodic"))
    assert c.source_url == "https://sodic.example/about"
    assert c.source_title == "سوديك"


def test_ready_doc_with_todo_is_refused(docs_root):
    p = docs_root / "areas" / "october_6.md"
    p.write_text(DRAFT.replace("status: draft", "status: ready").replace(
        "---\n## ", "sources:\n  - https://x.example\n---\n## ", 1), encoding="utf-8")
    docs, _ = load_docs(docs_root)
    with pytest.raises(DocError):
        chunk_doc(next(d for d in docs if d.entity_id == "october_6"))


def test_section_without_any_source_is_refused(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\ndoc_type: area_guide\nentity_id: x\ntitle: X\nstatus: ready\n---\n## h\nنص\n",
        encoding="utf-8",
    )
    docs, _ = load_docs(tmp_path)
    with pytest.raises(DocError):
        chunk_doc(docs[0])


def test_content_hash_changes_with_text(docs_root):
    docs, _ = load_docs(docs_root)
    d = next(x for x in docs if x.entity_id == "maadi")
    h1 = chunk_doc(d)[0].content_hash
    d.body = d.body.replace("هادي", "هادئ")
    assert chunk_doc(d)[0].content_hash != h1


def test_normalise_cuts_and_scales():
    v = normalise([3.0, 4.0] + [0.0] * (EMBED_DIM + 10))
    assert len(v) == EMBED_DIM
    assert v[0] == pytest.approx(0.6) and v[1] == pytest.approx(0.8)


def test_hash_embedder_is_deterministic():
    e = HashEmbedder()
    a, b = e.embed(["الشيخ زايد", "الشيخ زايد"])
    assert a == b and len(a) == EMBED_DIM


@pytest.fixture
def rag(docs_root):
    emb = HashEmbedder()
    return Rag(build_memory_index(docs_root, emb), emb)


def test_search_finds_the_right_guide(rag):
    assert rag.search("الشيخ زايد مناسبة للعائلات؟", k=1)[0].doc_id == "areas/sheikh_zayed"
    assert rag.search("سوديك شركة مقيدة في البورصة؟", k=1)[0].doc_id == "developers/sodic"
    assert rag.search("كورنيش النيل في المعادي", k=1)[0].doc_id == "areas/maadi"


def test_search_filters_by_entity(rag):
    hits = rag.search("مشروعات في زايد", k=4, entity_id="sodic")
    assert hits and all(h.entity_id == "sodic" for h in hits)


def test_every_hit_has_a_source(rag):
    for h in rag.search("مدينة", k=10):
        assert h.source_url.startswith("http")
        assert h.title


def test_empty_query_returns_nothing(rag):
    assert rag.search("   ") == []


def test_min_score_drops_weak_hits(docs_root):
    emb = HashEmbedder()
    rag = Rag(build_memory_index(docs_root, emb), emb, min_score=0.99)
    assert rag.search("سؤال عن حاجة تانية خالص") == []
