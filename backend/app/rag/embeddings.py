"""Text -> vector.

* ``GeminiEmbedder``: gemini-embedding-001 through the same OpenAI-compatible endpoint as
  app/agent/llm.py. Reads GEMINI_API_KEY (and optional GEMINI_EMBED_MODEL) from the
  environment. The full vector is cut to EMBED_DIM (768) and re-normalised; this model is
  trained so its first dimensions carry the meaning (Matryoshka).
* ``HashEmbedder``: deterministic, offline, no key. Bag of normalised words and character
  3-grams hashed into EMBED_DIM buckets. Good enough for tests and for running the demo
  without a key; not as good as Gemini on meaning.
"""

from __future__ import annotations

import hashlib
import logging
import math
import os
import re
import time
from collections.abc import Sequence
from typing import Protocol

logger = logging.getLogger(__name__)

EMBED_DIM = 768  # must match the vector(768) column in migration 0005
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_EMBED_MODEL = "gemini-embedding-001"
BATCH = 50


class Embedder(Protocol):
    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


def normalise(vec: Sequence[float], dim: int = EMBED_DIM) -> list[float]:
    """Cut to ``dim`` values and scale to length 1 (cosine-ready)."""
    v = list(vec[:dim])
    if len(v) < dim:
        raise ValueError(f"embedding has {len(v)} values, need at least {dim}")
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm > 0 else v


class GeminiEmbedder:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set (see .env.example)")
        self.model = model or os.getenv("GEMINI_EMBED_MODEL") or DEFAULT_EMBED_MODEL
        self.name = f"gemini:{self.model}:{EMBED_DIM}"
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI  # imported lazily: tests run without the package

            self._client = OpenAI(
                api_key=self.api_key, base_url=GEMINI_BASE_URL, timeout=30.0, max_retries=0
            )
        return self._client

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), BATCH):
            out.extend(self._embed_batch(list(texts[i : i + BATCH])))
        return out

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        import openai

        delays = [2.0, 5.0, 15.0, 30.0]  # free tier: back off on 429 instead of failing
        for attempt in range(len(delays) + 1):
            try:
                resp = self._get_client().embeddings.create(model=self.model, input=batch)
                data = sorted(resp.data, key=lambda d: d.index)
                return [normalise(d.embedding) for d in data]
            except (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError):
                if attempt == len(delays):
                    raise
                logger.warning("embedding retry %d after %.0fs", attempt + 1, delays[attempt])
                time.sleep(delays[attempt])
            except openai.APIStatusError as e:
                if e.status_code >= 500 and attempt < len(delays):
                    time.sleep(delays[attempt])
                    continue
                raise
        raise RuntimeError("unreachable")


_AR_DIACRITICS = re.compile(r"[ً-ْـ]")


def simplify(text: str) -> str:
    """Lowercase, drop Arabic diacritics/tatweel, unify alef/yaa/taa marbuta forms."""
    t = _AR_DIACRITICS.sub("", text.lower())
    t = re.sub("[إأآا]", "ا", t)
    t = t.replace("ى", "ي").replace("ة", "ه")
    return t


class HashEmbedder:
    name = f"hash:v1:{EMBED_DIM}"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vec = [0.0] * EMBED_DIM
        words = re.findall(r"\w+", simplify(text))
        feats: list[str] = []
        for w in words:
            if len(w) < 2:
                continue
            feats.append("w:" + w)
            if w.startswith("ال") and len(w) > 3:  # Arabic article: الشيخ ~ شيخ
                feats.append("w:" + w[2:])
            padded = f"#{w}#"
            feats.extend("g:" + padded[i : i + 3] for i in range(len(padded) - 2))
        for f in feats:
            h = int.from_bytes(hashlib.md5(f.encode()).digest()[:8], "big")
            vec[h % EMBED_DIM] += 1.0 if (h >> 63) == 0 else -1.0
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec


def default_embedder() -> Embedder:
    """Gemini when a key is configured, otherwise the offline HashEmbedder."""
    if os.getenv("GEMINI_API_KEY") and os.getenv("RAG_EMBEDDER", "gemini") == "gemini":
        return GeminiEmbedder()
    return HashEmbedder()
