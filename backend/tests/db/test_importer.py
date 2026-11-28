"""S2-M3-02 importer tests. The cleaning tests need no database."""

import os
from datetime import UTC, date, datetime

import pytest
from app.db.importer import (
    clean_delivery_date,
    clean_frequency,
    clean_number,
    database_url,
    import_rows,
    row_to_listing,
)
from sqlalchemy import create_engine, text

GOOD_ROW = {
    "listing_id": "TEST-001",
    "source_url": "https://example.com/unit/1",
    "collected_at": datetime(2026, 11, 24, tzinfo=UTC),
    "collected_by": "Member 3",
    "area": "Maadi",
    "developer": "Test Developer",
    "price_egp": "3,948,000",
    "area_sqm": 84.0,
    "delivery_date": "Q2 2028",
    "down_payment_pct": 0.0,
    "years": 10.0,
    "frequency": "Monthly ",
}


def test_blank_is_none_and_zero_stays_zero():
    assert clean_number(None) is None
    assert clean_number("  ") is None
    assert clean_number(0.0) == 0.0
    assert clean_number("3,948,000") == 3948000.0


def test_number_that_excel_turned_into_a_date_is_an_error():
    with pytest.raises(ValueError):
        clean_number(datetime(2026, 2, 3, tzinfo=UTC))


def test_frequency():
    assert clean_frequency("Monthly ") == "monthly"
    assert clean_frequency(None) is None
    with pytest.raises(ValueError):
        clean_frequency("yearly")


def test_delivery_date():
    assert clean_delivery_date("Q2 2028") == date(2028, 6, 30)
    assert clean_delivery_date(2028.0) == date(2028, 12, 31)
    assert clean_delivery_date("Delivered") is None


def test_good_row():
    listing, errors = row_to_listing(10, GOOD_ROW)
    assert errors == []
    assert listing.area == "maadi"
    assert listing.down_payment_pct == 0.0       # a real zero stays zero
    assert listing.delivery_payment_pct is None  # blank stays unknown


def test_blank_plan_fields_are_none_not_zero():
    row = dict(GOOD_ROW, frequency=None, years=None, down_payment_pct=None)
    listing, errors = row_to_listing(11, row)
    assert errors == []
    assert listing.frequency is None and listing.years is None
    assert listing.down_payment_pct is None


def test_bad_row_lists_every_reason():
    row = dict(GOOD_ROW, area="Atlantis", price_egp=None)
    listing, errors = row_to_listing(7, row)
    assert listing is None
    assert "row 7: area unknown ('Atlantis')" in errors
    assert "row 7: price_egp missing" in errors


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="needs DATABASE_URL")
def test_second_run_changes_nothing():
    engine = create_engine(database_url())
    rows = [GOOD_ROW, dict(GOOD_ROW, listing_id="TEST-002", area=None)]
    try:
        first = import_rows(rows, engine)
        second = import_rows(rows, engine)
        assert first.accepted == 1 and first.rejected == 1
        assert first.errors == ["row 2: area missing"]
        assert second.data_version == first.data_version
    finally:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM listings WHERE listing_id LIKE 'TEST-%'"))
            conn.execute(text("DELETE FROM developers WHERE name = 'Test Developer'"))