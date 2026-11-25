"""S0-T4-2: check every mock file against its Pydantic model in backend/app/contracts.py.

Usage (from the repo root):
    python scripts/validate_fixtures.py                 # checks frontend/mocks/
    python scripts/validate_fixtures.py path/to/dir     # checks another folder

The model is chosen from the file name: ``<kind>.json`` or ``<kind>.<variant>.json``,
for example ``plan_result.zero_down.json`` is checked as a ``PlanResult``.
A file whose kind is not in MODELS fails; nothing is skipped silently.

Prints ``OK`` or ``FAIL`` with the error for each file. Exit code 0 only when at least one
file was checked and every file passed; otherwise 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.contracts import (
    AffordabilityResult,
    LeadBrief,
    LeadState,
    Listing,
    PaymentPlan,
    PlanResult,
    SearchResult,
)
from pydantic import TypeAdapter, ValidationError

DEFAULT_DIR = ROOT / "frontend" / "mocks"

# file kind -> model. Lists use TypeAdapter so the whole list is checked.
MODELS: dict[str, TypeAdapter] = {
    "lead_state": TypeAdapter(LeadState),
    "lead_detail": TypeAdapter(LeadBrief),
    "leads": TypeAdapter(list[LeadBrief]),
    "search_result": TypeAdapter(SearchResult),
    "listing": TypeAdapter(Listing),
    "payment_plan": TypeAdapter(PaymentPlan),
    "plan_result": TypeAdapter(PlanResult),
    "affordability": TypeAdapter(AffordabilityResult),
}


def kind_of(path: Path) -> str:
    return path.name.split(".", 1)[0]


def check_file(path: Path) -> str | None:
    """Return None when the file is valid, or the error text."""
    adapter = MODELS.get(kind_of(path))
    if adapter is None:
        return f"no model for kind '{kind_of(path)}' (known: {', '.join(sorted(MODELS))})"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return f"not valid UTF-8 JSON: {exc}"
    try:
        adapter.validate_python(data)
    except ValidationError as exc:
        return str(exc)
    return None


def main(argv: list[str]) -> int:
    folder = Path(argv[1]) if len(argv) > 1 else DEFAULT_DIR
    files = sorted(folder.glob("*.json"))
    if not files:
        print(f"FAIL no .json files in {folder}")
        return 1

    failed = 0
    for path in files:
        error = check_file(path)
        if error is None:
            print(f"OK   {path.name}")
        else:
            failed += 1
            print(f"FAIL {path.name}: {error}")
    print(f"{len(files) - failed} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
