"""S2-M3-02: load AqarAI_listings.xlsx into Postgres.

Usage (from the repo root, with DATABASE_URL set):

    python scripts/ingest_listings.py path/to/AqarAI_listings.xlsx

Reads the "raw" sheet. The header is the row whose first cell is "source_url"
(the rows above it are instructions). Empty rows are skipped.
Running it twice with the same file changes nothing: data_version stays the same.
"""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))  # so "import app..." works from the repo root

from app.db.importer import import_rows, row_to_listing
from openpyxl import load_workbook

SHEET_NAME = "raw"


def read_rows(path: str) -> list[dict]:
    """Every non-empty row under the header, as {column: value, "row_number": n}."""
    workbook = load_workbook(path, data_only=True, read_only=True)
    sheet = workbook[SHEET_NAME]
    header = None
    rows = []
    for row_number, cells in enumerate(sheet.iter_rows(values_only=True), start=1):
        if header is None:
            if cells and cells[0] == "source_url":
                header = [str(c).strip() if c is not None else None for c in cells]
            continue
        if all(c is None or str(c).strip() == "" for c in cells):
            continue
        row = {name: value for name, value in zip(header, cells) if name}
        row["row_number"] = row_number
        rows.append(row)
    workbook.close()
    if header is None:
        raise SystemExit(f"No header row starting with 'source_url' in sheet {SHEET_NAME!r}")
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    rows = read_rows(sys.argv[1])

    # Count accepted rows per area (same check the importer does).
    per_area = Counter()
    for row in rows:
        listing, _ = row_to_listing(row["row_number"], row)
        if listing is not None:
            per_area[listing.area] += 1

    report = import_rows(rows)

    print(f"rows read:    {len(rows)}")
    print(f"accepted:     {report.accepted}")
    print(f"rejected:     {report.rejected}")
    print(f"data_version: {report.data_version}")
    print("\naccepted per area:")
    for area, count in sorted(per_area.items()):
        print(f"  {area}: {count}")
    if report.errors:
        print("\nrejected rows:")
        for error in report.errors:
            print(f"  {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())