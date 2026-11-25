"""S1-T10-2: Arabic text cleanup and area-name synonyms.

Pure code: no LLM call, no network call. The extract node (S1-T10-1), the search
filters and the retriever use these functions so that one area written many ways
becomes one canonical area id.

``normalize_text`` is for matching and search keys, not for showing text to the
customer: it changes letters (for example ``ة`` becomes ``ه``).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

SYNONYMS_FILE = Path(__file__).parent / "data" / "area_synonyms.json"

# Character maps, applied with str.translate (one pass, no regex per letter).
_ALEF = {c: "ا" for c in "أإآٱ"}                       # hamza above/below, madda, wasla
_YA = {"ى": "ي", "ی": "ي"}                              # alef maqsura, Persian ya
_TA_MARBUTA = {"ة": "ه"}
_KAF = {"ک": "ك"}                                       # Persian kaf (keyboard variant)
_DIGITS = {
    **{chr(0x0660 + i): str(i) for i in range(10)},    # Arabic-Indic ٠١٢٣٤٥٦٧٨٩
    **{chr(0x06F0 + i): str(i) for i in range(10)},    # Eastern Arabic-Indic ۰۱۲۳۴۵۶۷۸۹
}
_REMOVE = {
    "\u0640": None,                                     # tatweel (ـ)
    **{chr(c): None for c in range(0x064B, 0x0660)},    # tashkeel: fathatan .. wavy hamza
    "\u0670": None,                                     # superscript alef
    # Invisible direction marks that come with copy-paste from RTL apps.
    **{c: None for c in "\u200c\u200d\u200e\u200f\u061c\u202a\u202b\u202c\u202d\u202e\ufeff"},
}
_TABLE = str.maketrans({**_ALEF, **_YA, **_TA_MARBUTA, **_KAF, **_DIGITS, **_REMOVE})

_SPACES = re.compile(r"\s+")
# Punctuation that only separates words in an area name: hyphens, dashes, dots, commas, quotes.
_SEPARATORS = re.compile(r"[-\u2010-\u2015_.,\u060c'\"()/]+")


def normalize_text(text: str | None) -> str | None:
    """Clean Arabic text for matching.

    * unify alef variants (أ إ آ ٱ -> ا), ya (ى ی -> ي) and ta marbuta (ة -> ه)
    * remove tashkeel (diacritics), tatweel and invisible direction marks
    * convert Arabic-Indic digits (٠-٩ and ۰-۹) to 0-9
    * collapse all whitespace to single spaces and trim

    ``None`` stays ``None``. Latin letters are not lowercased here.
    """
    if text is None:
        return None
    return _SPACES.sub(" ", text.translate(_TABLE)).strip()


def _match_key(text: str) -> str:
    """The form used to compare area names: normalized, lowercase, no separators."""
    cleaned = normalize_text(text) or ""
    return _SPACES.sub(" ", _SEPARATORS.sub(" ", cleaned.casefold())).strip()


def load_synonyms(path: Path = SYNONYMS_FILE) -> dict[str, str]:
    """Read the synonyms file into ``{match_key: area_id}``.

    Raises ``ValueError`` if one spelling points to two different areas, or if an
    entry is empty after cleanup, so a bad data file fails in CI, not in a chat.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    table: dict[str, str] = {}
    for area in data["areas"]:
        area_id = area["id"]
        for name in [area["name_ar"], area["name_en"], *area["synonyms"]]:
            key = _match_key(name)
            if not key:
                raise ValueError(f"empty synonym for area {area_id!r}: {name!r}")
            other = table.get(key)
            if other is not None and other != area_id:
                raise ValueError(f"synonym {name!r} maps to both {other!r} and {area_id!r}")
            table[key] = area_id
    return table


@lru_cache(maxsize=1)
def _synonyms() -> dict[str, str]:
    return load_synonyms()


def normalize_area(text: str | None) -> str | None:
    """Return the canonical area id for an area name, or ``None`` if it is not in our list.

    The whole text must match one known spelling. There is no fuzzy or "closest"
    match on purpose: a wrong area is worse than asking the customer again.
    """
    if text is None:
        return None
    key = _match_key(text)
    if not key:
        return None
    return _synonyms().get(key)
