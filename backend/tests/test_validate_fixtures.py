"""S0-T4-2: tests for scripts/validate_fixtures.py and the mock files.

The script and the mocks are checked against contracts written by other members
(LeadState, LeadBrief, Listing, SearchResult, PaymentPlan), so a contract change that
breaks the frontend mocks fails here.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "validate_fixtures.py"
MOCKS = ROOT / "frontend" / "mocks"
BAD = Path(__file__).parent / "fixtures_bad"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], check=False,
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


@pytest.fixture(scope="module")
def script():
    spec = importlib.util.spec_from_file_location("validate_fixtures", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mock(name: str):
    return json.loads((MOCKS / name).read_text(encoding="utf-8"))


# ---------- the real mocks ----------

def test_all_mocks_pass():
    result = run()
    assert result.returncode == 0, result.stdout
    assert "0 failed" in result.stdout
    assert "FAIL" not in result.stdout


def test_every_mock_has_a_model(script):
    for path in MOCKS.glob("*.json"):
        assert script.kind_of(path) in script.MODELS, path.name


# The edge cases the task asks the mocks to show.

def test_mock_none_and_zero_are_different():
    plan = mock("plan_result.delivery_unknown.json")
    zero = mock("plan_result.zero_down.json")
    assert plan["delivery_payment_egp"] is None and plan["payments"] is None
    assert zero["delivery_payment_egp"] == 0.0 and zero["payments"]


def test_mock_zero_down_plan():
    assert mock("payment_plan.zero_down.json")["down_payment_pct"] == 0.0
    rows = mock("plan_result.zero_down.json")["payments"]
    assert rows[0] == {"month": 0, "amount_egp": 0.0, "type": "down_payment"}


def test_mock_empty_plan_has_only_required_fields():
    assert set(mock("payment_plan.empty.json")) == {"plan_id", "years", "frequency"}


def test_mock_missing_delivery_payment_is_recorded():
    plan = mock("plan_result.delivery_unknown.json")
    assert plan["missing_fields"] == ["delivery_payment_egp"]
    assert plan["warnings"] == ["delivery_payment_unknown"]


def test_mock_arabic_indic_digits_only_in_text():
    notes = mock("listing.json")["notes"]
    assert any("٠" <= ch <= "٩" for ch in notes)


def test_mocks_have_arabic_text_and_no_personal_data():
    text = "".join(p.read_text(encoding="utf-8") for p in MOCKS.glob("*.json"))
    assert any("؀" <= ch <= "ۿ" for ch in text)        # Arabic text present
    assert "example.invalid" in text                              # fake source URLs only
    for marker in ("+20", "phone", "@gmail", "@yahoo", "http://"):
        assert marker not in text


def test_leads_are_sorted_by_score():
    scores = [lead["score"] for lead in mock("leads.json")]
    assert scores == sorted(scores, reverse=True)


# ---------- deliberately bad files ----------

EXPECTED_ERRORS = {
    "plan_result.unknown_delivery_written_as_zero.json": "delivery_payment_egp is unknown",
    "plan_result.empty_payment_table.json": "payments is empty",
    "listing.arabic_indic_price.json": "unable to parse string as a number",
    "affordability.reason_with_numbers.json": "must not contain numbers",
    "affordability.unknown_gap_written_as_zero.json": "one of its inputs is None",
    "payment_plan.zero_without_source.json": "down_payment_source is required",
    "search_result.bad_frequency.json": "'monthly' or 'quarterly'",
    "leads.not_a_list.json": "valid list",
    "conversation.json": "no model for kind 'conversation'",
    "lead_detail.broken.json": "not valid UTF-8 JSON",
}


def test_bad_folder_fails_with_exit_code_1():
    result = run(str(BAD))
    assert result.returncode == 1
    assert f"0 ok, {len(EXPECTED_ERRORS)} failed" in result.stdout


@pytest.mark.parametrize(("name", "expected"), sorted(EXPECTED_ERRORS.items()))
def test_each_bad_file_fails_for_the_right_reason(script, name, expected):
    error = script.check_file(BAD / name)
    assert error is not None
    assert expected in error


def test_every_bad_file_is_listed():
    assert {p.name for p in BAD.glob("*.json")} == set(EXPECTED_ERRORS)


def test_one_bad_file_among_good_ones_fails(tmp_path):
    for path in MOCKS.glob("*.json"):
        shutil.copy(path, tmp_path)
    shutil.copy(BAD / "plan_result.empty_payment_table.json", tmp_path)
    result = run(str(tmp_path))
    assert result.returncode == 1
    assert "1 failed" in result.stdout


def test_empty_folder_fails(tmp_path):
    result = run(str(tmp_path))
    assert result.returncode == 1
    assert "no .json files" in result.stdout


def test_windows_line_endings_still_pass(tmp_path):
    src = MOCKS / "lead_detail.json"
    (tmp_path / src.name).write_bytes(src.read_bytes().replace(b"\n", b"\r\n"))
    assert run(str(tmp_path)).returncode == 0
