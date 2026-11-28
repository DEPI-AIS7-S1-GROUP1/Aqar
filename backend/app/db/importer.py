"""S2-M3-02 import listing rows (from the Excel sheet or an uploaded file) into Postgres.

import_rows(rows) is used by scripts/ingest_listings.py now and by the import endpoint
(S2-M3-03) later. Each row is a dict {column name: cell value} from the sheet.

Rules:
* A blank cell becomes None, never 0. A real 0 in the sheet stays 0.
* The area goes through normalize_area(). An unknown area rejects the row.
* Required fields come from the Listing contract. If the contract makes a field
  optional later, this file does not need to change.
* verified_by is NOT checked (team decision 27 Nov: no rows are verified yet).
  The column is kept: NULL means not verified.
* Everything is written in one transaction. Rows that did not change are not
  rewritten, and data_meta.data_version is bumped only when something changed,
  so running the same file twice changes nothing.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime

from pydantic import ValidationError
from sqlalchemy import Engine, create_engine, text

from app.agent.normalize import normalize_area
from app.contracts import ImportReport, Listing, PaymentPlan

# Listing fields that are also columns of the listings table, in table order.
LISTING_COLUMNS = [
    "listing_id", "source_url", "collected_at", "collected_by", "verified_by",
    "area", "developer", "price_egp", "area_sqm", "delivery_date",
    "down_payment_pct", "years", "frequency", "delivery_payment_pct",
    "maintenance_pct", "notes",
    "title", "unit_type", "bedrooms", "image_urls", "image_credit",
]

# Fields a source may not publish. Their names go in listings.missing_fields when None.
PUBLISHABLE_FIELDS = [
    "developer", "delivery_date", "down_payment_pct", "years",
    "frequency", "delivery_payment_pct", "maintenance_pct", "bedrooms",
]

PLAN_COLUMNS = [
    "plan_id", "listing_id", "down_payment_egp", "down_payment_pct",
    "down_payment_source", "years", "frequency", "delivery_payment_pct",
    "delivery_month", "maintenance_pct",
]


# ---------- 1. cleaning one cell ----------

def clean_text(value) -> str | None:
    """Blank or only spaces -> None. Anything else -> stripped text."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def clean_datetime(value) -> datetime | str | None:
    """A real Excel date stays a datetime. Text like "2026-11-24" is left for
    pydantic to parse (it reports a clear error if the text is not a date)."""
    if isinstance(value, datetime):
        return value
    return clean_text(value)


def clean_number(value) -> float | None:
    """84.0, "3,948,000", " 43.38 " -> float. Blank -> None. Not a number -> ValueError."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        # Excel turned the number into a date. Fix the cell in the sheet.
        raise ValueError(f"is a date ({value:%Y-%m-%d}), expected a number")  # noqa: TRY004
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).strip().replace(",", "")
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"is not a number ({value!r})") from None


def clean_int(value) -> int | None:
    """Like clean_number, but the number must be whole (10.0 is fine, 10.5 is not)."""
    number = clean_number(value)
    if number is None:
        return None
    if not number.is_integer():
        raise ValueError(f"must be a whole number ({value!r})")
    return int(number)


def clean_frequency(value) -> str | None:
    """"Monthly", "monthly " -> "monthly". Blank -> None. Anything else -> ValueError."""
    value = clean_text(value)
    if value is None:
        return None
    value = value.lower()
    if value not in ("monthly", "quarterly"):
        raise ValueError(f"must be monthly or quarterly ({value!r})")
    return value


QUARTER_END = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def clean_delivery_date(value) -> date | None:
    """Turn the sheet's delivery text into a date we can filter on (delivery_date <= X).

    A real date -> that date.
    2028 or "2028" -> 31 Dec 2028 (the latest day the source allows).
    "Q2 2028" -> 30 Jun 2028 (end of that quarter).
    Anything else ("Delivered", "3 years from launch", blank) -> None (unknown).
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and float(value).is_integer() and 2000 <= value <= 2100:
        return date(int(value), 12, 31)

    text_value = str(value).strip().upper()
    if re.fullmatch(r"\d{4}", text_value):
        return date(int(text_value), 12, 31)
    quarter = re.fullmatch(r"Q([1-4])\s*(\d{4})", text_value)
    if quarter:
        month, day = QUARTER_END[int(quarter.group(1))]
        return date(int(quarter.group(2)), month, day)
    try:
        return date.fromisoformat(text_value)
    except ValueError:
        return None


def clean_image_urls(value) -> list[str] | None:
    """"/listings/A/1.webp;/listings/A/2.webp" -> list. Blank -> None."""
    value = clean_text(value)
    if value is None:
        return None
    urls = [url.strip() for url in value.split(";") if url.strip()]
    return urls or None


# Which cleaner each sheet column uses.
CLEANERS = {
    "listing_id": clean_text,
    "source_url": clean_text,
    "collected_at": clean_datetime,
    "collected_by": clean_text,
    "verified_by": clean_text,
    "area": clean_text,
    "developer": clean_text,
    "price_egp": clean_number,
    "area_sqm": clean_number,
    "delivery_date": clean_delivery_date,
    "down_payment_pct": clean_number,
    "years": clean_int,
    "frequency": clean_frequency,
    "delivery_payment_pct": clean_number,
    "maintenance_pct": clean_number,
    "notes": clean_text,
    "title": clean_text,
    "unit_type": clean_text,
    "bedrooms": clean_int,
    "image_urls": clean_image_urls,
    "image_credit": clean_text,
}


# ---------- 2. one row -> Listing (or the reasons it was rejected) ----------

def required_fields() -> list[str]:
    """Fields the Listing contract requires, plus listing_id (the database key)."""
    names = [name for name, field in Listing.model_fields.items() if field.is_required()]
    return ["listing_id"] + names


def row_to_listing(row_number: int, row: dict) -> tuple[Listing | None, list[str]]:
    """Return (listing, []) for a good row, or (None, ["row 7: price_egp missing", ...])."""
    errors = []
    bad_columns = set()  # columns that already have an error, so we report them once
    values = {}

    for column, cleaner in CLEANERS.items():
        try:
            values[column] = cleaner(row.get(column))
        except ValueError as problem:
            errors.append(f"row {row_number}: {column} {problem}")
            bad_columns.add(column)
            values[column] = None

    if values["area"] is not None:
        area_id = normalize_area(values["area"])
        if area_id is None:
            errors.append(f"row {row_number}: area unknown ({values['area']!r})")
            bad_columns.add("area")
        values["area"] = area_id

    for name in required_fields():
        if values.get(name) is None and name not in bad_columns:
            errors.append(f"row {row_number}: {name} missing")

    if errors:
        return None, errors

    try:
        return Listing(**values), []
    except ValidationError as problem:
        for error in problem.errors():
            field = ".".join(str(part) for part in error["loc"]) or "row"
            errors.append(f"row {row_number}: {field} {error['msg']}")
        return None, errors


def plan_from_listing(listing: Listing) -> PaymentPlan | None:
    """The sheet has one plan per unit, written on the listing row.
    None if the plan terms (years, frequency) are unknown."""
    if listing.years is None or listing.frequency is None:
        return None
    return PaymentPlan(
        plan_id=f"{listing.listing_id}-1",
        down_payment_pct=listing.down_payment_pct,
        down_payment_source=None if listing.down_payment_pct is None else "pct",
        years=listing.years,
        frequency=listing.frequency,
        delivery_payment_pct=listing.delivery_payment_pct,
        maintenance_pct=listing.maintenance_pct,
    )


# ---------- 3. write everything in one transaction ----------

def database_url() -> str:
    """Same rule as the Alembic env: DATABASE_URL, using the psycopg 3 driver."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set (see .env.example)")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def upsert_sql(table: str, columns: list[str], key: str) -> str:
    """INSERT ... ON CONFLICT (key) DO UPDATE, but only if a value really changed.
    An unchanged row is not touched, so it does not count as a change."""
    names = ", ".join(columns)
    params = ", ".join(f":{c}" for c in columns)
    others = [c for c in columns if c != key]
    updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in others)
    old_values = ", ".join(f"{table}.{c}" for c in others)
    new_values = ", ".join(f"EXCLUDED.{c}" for c in others)
    return (
        f"INSERT INTO {table} ({names}) VALUES ({params}) "
        f"ON CONFLICT ({key}) DO UPDATE SET {updates} "
        f"WHERE ({old_values}) IS DISTINCT FROM ({new_values})"
    )


def import_rows(rows: list[dict], engine: Engine | None = None) -> ImportReport:
    """Validate every row, write the good ones, report the bad ones.

    Each row may carry "row_number" (the sheet row) so errors point to the right line.
    Otherwise rows are numbered from 1.
    """
    good: list[Listing] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, row in enumerate(rows, start=1):
        row_number = row.get("row_number", index)
        listing, row_errors = row_to_listing(row_number, row)
        if listing is not None and listing.listing_id in seen_ids:
            row_errors = [f"row {row_number}: listing_id {listing.listing_id!r} is used twice"]
            listing = None
        if listing is None:
            errors.extend(row_errors)
        else:
            seen_ids.add(listing.listing_id)
            good.append(listing)

    rejected = len(rows) - len(good)
    engine = engine or create_engine(database_url())
    listing_sql = text(upsert_sql("listings", LISTING_COLUMNS + ["missing_fields"], "listing_id"))
    plan_sql = text(upsert_sql("payment_plans", PLAN_COLUMNS, "plan_id"))

    with engine.begin() as conn:  # one transaction: all rows or nothing
        changes = 0
        for listing in good:
            if listing.developer is not None: 
                result = conn.execute(
                    text("INSERT INTO developers (name) VALUES (:name) "
                         "ON CONFLICT (name) DO NOTHING"),
                    {"name": listing.developer},
                )
                changes += result.rowcount

            values = {c: getattr(listing, c) for c in LISTING_COLUMNS}
            values["missing_fields"] = [f for f in PUBLISHABLE_FIELDS
                                        if getattr(listing, f) is None]
            changes += conn.execute(listing_sql, values).rowcount

            plan = plan_from_listing(listing)
            if plan is not None:
                plan_values = {c: getattr(plan, c, None) for c in PLAN_COLUMNS}
                plan_values["listing_id"] = listing.listing_id
                changes += conn.execute(plan_sql, plan_values).rowcount

        if changes > 0:
            data_version = conn.execute(text(
                "UPDATE data_meta SET data_version = data_version + 1 "
                "WHERE id = 1 RETURNING data_version")).scalar_one()
        else:
            data_version = conn.execute(text(
                "SELECT data_version FROM data_meta WHERE id = 1")).scalar_one()

    return ImportReport(accepted=len(good), rejected=rejected,
                        errors=errors, data_version=data_version)