"""S1-T10-2: tests for normalize_text() and normalize_area()."""

import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.agent.normalize import (
    SYNONYMS_FILE,
    load_synonyms,
    normalize_area,
    normalize_text,
)

# ---------- normalize_text ----------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("أحمد", "احمد"),                   # alef with hamza above
        ("إدارية", "اداريه"),               # hamza below + ta marbuta
        ("آمن", "امن"),                     # alef madda
        ("ٱلقاهرة", "القاهره"),             # alef wasla
        ("مستشفى", "مستشفي"),               # alef maqsura -> ya
        ("القَاهِرَةُ", "القاهره"),          # tashkeel removed
        ("شـــقة", "شقه"),                  # tatweel removed
        ("٣ غرف", "3 غرف"),                 # Arabic-Indic digit
        ("۲۵۰۰۰۰۰", "2500000"),             # Eastern Arabic-Indic (Persian) digits
        ("١٢٣٤٥٦٧٨٩٠", "1234567890"),
        ("٢٫٥ مليون", "2.5 مليون"),         # Arabic decimal separator
        ("٢٬٥٠٠٬٠٠٠", "2,500,000"),         # Arabic thousands separator
        ("  شقة   في\tالتجمع \n", "شقه في التجمع"),   # spaces trimmed and collapsed
        ("\u200fالتجمع\u200e", "التجمع"),   # invisible RTL/LTR marks removed
        ("New Cairo", "New Cairo"),         # Latin text is left as it is
        ("", ""),
    ],
)
def test_normalize_text(raw, expected):
    assert normalize_text(raw) == expected


def test_normalize_text_none_stays_none():
    assert normalize_text(None) is None


def test_normalize_text_is_idempotent():
    once = normalize_text("العاصِمة الإداريـة ٢٠٢٦")
    assert normalize_text(once) == once


def test_digits_are_text_not_numbers():
    # The normalizer only rewrites characters. Turning "٢٥٠٠٠٠٠" into a price is the
    # extractor's job, in code, never the LLM's.
    out = normalize_text("٢٥٠٠٠٠٠")
    assert isinstance(out, str)
    assert out == "2500000"


# ---------- normalize_area: same area, many spellings ----------

SAME_AREA = {
    "new_cairo": [
        "القاهرة الجديدة", "القاهره الجديده", "القاهرةُ الجديدةُ", "التجمع",
        "التجمع الخامس", "التجمع ٥", "التجمع 5", "التجمّع الخامس", "الخامس",
        "New Cairo", "new cairo", "NEW  CAIRO", "Fifth Settlement", "5th settlement",
        "Tagamoa", "tagamo3", "El-Tagamoa El-Khames",
    ],
    "sheikh_zayed": [
        "الشيخ زايد", "الشيخ  زايد", "زايد", "مدينة الشيخ زايد",
        "Sheikh Zayed", "El Sheikh Zayed", "sheikh-zayed", "zayed",
    ],
    "october_6": [
        "6 أكتوبر", "٦ أكتوبر", "6 اكتوبر", "٦ اكتوبر", "السادس من أكتوبر",
        "أكتوبر", "6th of October", "6 October", "October",
    ],
    "new_capital": [
        "العاصمة الإدارية", "العاصمه الاداريه", "العاصمة الإدارية الجديدة",
        "العاصمة", "New Capital", "New Administrative Capital", "NAC",
    ],
    "mostakbal_city": ["مستقبل سيتي", "مستقبل سيتى", "Mostakbal City", "Future City"],
    "north_coast_ras_el_hekma": [
        "الساحل الشمالي – رأس الحكمة", "الساحل الشمالى - راس الحكمه", "رأس الحكمة",
        "راس الحكمه", "الساحل", "Ras El Hekma", "North Coast", "Sahel",
    ],
        "maadi": [
        "المعادي", "المعادى", "معادي", "حي المعادي", "كورنيش المعادي",
        "Maadi", "El Maadi", "al-maadi", "New Maadi", "Maadi Degla", "Hay El Maadi",
    ],
}


@pytest.mark.parametrize(
    ("area_id", "spelling"),
    [(area_id, s) for area_id, spellings in SAME_AREA.items() for s in spellings],
)
def test_spellings_map_to_one_id(area_id, spelling):
    assert normalize_area(spelling) == area_id


def test_every_area_in_the_data_file_is_tested():
    data = json.loads(SYNONYMS_FILE.read_text(encoding="utf-8"))
    assert {a["id"] for a in data["areas"]} == set(SAME_AREA)


def test_every_listed_synonym_resolves_to_its_area():
    data = json.loads(SYNONYMS_FILE.read_text(encoding="utf-8"))
    for area in data["areas"]:
        for name in [area["name_ar"], area["name_en"], *area["synonyms"]]:
            assert normalize_area(name) == area["id"], name


# ---------- normalize_area: unknown text returns None, no guessing ----------


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        "   ",
        "زهراء المعادي",              # Zahraa El Maadi is a different district from Maadi
        "Degla",                      # could be Degla (Maadi) or Degla Palms (6 October)
        "حدائق أكتوبر",               # October Gardens is a different place from 6 October
        "الشيخ زايد الجديدة",          # New Zayed is a different city
        "التجمع الأول",               # First Settlement: not in our list yet, do not guess
        "القاهرة",                    # Cairo is not New Cairo
        "التجمع الخامس او زايد",      # two areas: the extractor must split them first
        "عايز شقة في التجمع",          # a whole sentence: the extractor passes the area only
        "new cairoo",                 # typo: no fuzzy match
        "المستقبل",
        "0",
    ],
)
def test_unknown_text_returns_none(text):
    assert normalize_area(text) is None


# ---------- data file checks ----------


def test_conflicting_synonym_is_rejected(tmp_path):
    bad = {
        "areas": [
            {"id": "a", "name_ar": "التجمع", "name_en": "A", "synonyms": []},
            {"id": "b", "name_ar": "التجمّع", "name_en": "B", "synonyms": []},  # same after cleanup
        ]
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="maps to both"):
        load_synonyms(path)


def test_empty_synonym_is_rejected(tmp_path):
    bad = {"areas": [{"id": "a", "name_ar": "ـــ", "name_en": "A", "synonyms": []}]}
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="empty synonym"):
        load_synonyms(path)


def test_shipped_data_file_loads():
    table = load_synonyms()
    assert len(set(table.values())) == len(SAME_AREA)


@pytest.mark.parametrize("text", ["التجمع؟", "التجمع!", "new cairo?", "زايد؛", "Zayed!",])
def test_trailing_question_or_exclamation_mark_still_matches(text):
    assert normalize_area(text) is not None
