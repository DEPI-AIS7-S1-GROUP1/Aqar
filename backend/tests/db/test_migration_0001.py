"""S1-T2-1: checks for the first Alembic migration.

Static part (always runs, no database): the migration's columns are compared with the
``Listing`` and ``PaymentPlan`` contracts written by other members.

Live part (runs only when TEST_DATABASE_URL is set): upgrade, downgrade, upgrade again on
a throwaway database, then insert rows to check NULL vs 0 and the CHECK constraints.
Never point TEST_DATABASE_URL at a database you care about: the test drops the tables.
"""

import importlib.util
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import sqlalchemy as sa

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.contracts import Listing, PaymentPlan

MIGRATION = BACKEND / "app/db/migrations/versions/0001_listings_developers_payment_plans.py"

# Columns that are in the database but not in the contract, on purpose.
# Made nullable later by migration 0006. In 0001 they are still NOT NULL.
NULLABLE_SINCE_0006 = {"developer", "area_sqm", "down_payment_pct", "years", "frequency"}
# contracts-v2 fields added by migration 0003 (tested in test_migration_0003.py).
LISTING_FIELDS_FROM_0003 = {"title", "unit_type", "bedrooms", "image_urls", "image_credit"}
LISTING_HELPERS = {"missing_fields", "data_version"}
PLAN_HELPERS = {"listing_id"}          # the reference to listings (task sheet step 2)

NEEDS_S0_T3_4 = pytest.mark.skipif(
    "plan_id" not in PaymentPlan.model_fields,
    reason="needs the S0-T3-4 contracts (PaymentPlan.plan_id, Listing.listing_id)",
)


class _Recorder:
    """Stands in for alembic.op and keeps the tables the migration creates."""

    def __init__(self) -> None:
        self.tables: dict[str, dict[str, sa.Column]] = {}
        self.indexes: dict[str, list[str]] = {}

    def create_table(self, name, *items):
        self.tables[name] = {c.name: c for c in items if isinstance(c, sa.Column)}

    def create_index(self, name, table, columns):
        self.indexes[name] = [table, *columns]


@pytest.fixture(scope="module")
def recorded() -> _Recorder:
    spec = importlib.util.spec_from_file_location("migration_0001", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rec = _Recorder()
    module.op = rec
    module.upgrade()
    return rec


def _check_against(model, columns, helpers, keys):
    fields = {n: f for n, f in model.model_fields.items() if n not in LISTING_FIELDS_FROM_0003}
    assert set(columns) - helpers == set(fields), "columns must match the contract field by field"
    for name, info in fields.items():
        col = columns[name]
        if name in keys:
            assert not col.nullable      # primary key, see migration comment
            continue
        if name not in NULLABLE_SINCE_0006:
            assert col.nullable == (not info.is_required()), f"{name}: nullable must follow the contract"
        assert col.server_default is None, f"{name}: no database default (never 0 for unknown)"

@NEEDS_S0_T3_4
def test_listings_match_listing_contract(recorded):
    _check_against(Listing, recorded.tables["listings"], LISTING_HELPERS, {"listing_id"})


@NEEDS_S0_T3_4
def test_payment_plans_match_payment_plan_contract(recorded):
    _check_against(PaymentPlan, recorded.tables["payment_plans"], PLAN_HELPERS, {"plan_id"})


def test_tables_created_in_dependency_order(recorded):
    assert list(recorded.tables) == ["developers", "listings", "payment_plans"]


def test_listing_helper_columns(recorded):
    cols = recorded.tables["listings"]
    for name in ("source_url", "collected_at", "verified_by", "missing_fields", "data_version"):
        assert name in cols
    assert not cols["source_url"].nullable
    assert not cols["collected_at"].nullable
    assert cols["data_version"].nullable


def test_money_and_percent_are_numeric_not_float(recorded):
    for table in ("listings", "payment_plans"):
        for name, col in recorded.tables[table].items():
            if name.endswith(("_egp", "_pct")):
                assert isinstance(col.type, sa.Numeric) and not isinstance(col.type, sa.Float), name


def test_no_numeric_column_has_a_default(recorded):
    for table in ("listings", "payment_plans"):
        for name, col in recorded.tables[table].items():
            if isinstance(col.type, (sa.Numeric, sa.Integer)):
                assert col.server_default is None, f"{table}.{name}"


def test_search_indexes(recorded):
    indexed = {tuple(v) for v in recorded.indexes.values()}
    for column in ("area", "price_egp", "delivery_date", "developer"):
        assert ("listings", column) in indexed


# ---------- live database (optional) ----------

LIVE_URL = os.environ.get("TEST_DATABASE_URL")
live = pytest.mark.skipif(not LIVE_URL, reason="TEST_DATABASE_URL not set")


def _alembic(*args: str) -> None:
    env = {**os.environ, "DATABASE_URL": LIVE_URL}
    subprocess.run([sys.executable, "-m", "alembic", *args], cwd=BACKEND, env=env, check=True)


@pytest.fixture(scope="module")
def engine():
    url = LIVE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    eng = sa.create_engine(url)
    _alembic("downgrade", "base")
    _alembic("upgrade", "head")
    _alembic("downgrade", "-1")
    _alembic("upgrade", "head")
    yield eng
    _alembic("downgrade", "base")
    eng.dispose()


LISTING = {
    "listing_id": "lst_test_1", "source_url": "https://example.invalid/unit/1",
    "collected_at": datetime(2026, 11, 20, tzinfo=UTC), "collected_by": "member_x",
    "area": "new_cairo", "developer": "Example Developer", "price_egp": 5_000_000,
    "area_sqm": 150, "down_payment_pct": 10, "years": 8, "frequency": "quarterly",
}


def _insert(conn, table: str, row: dict) -> None:
    cols = ", ".join(row)
    vals = ", ".join(f":{k}" for k in row)
    conn.execute(sa.text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), row)


@live
def test_live_null_stays_null_and_zero_stays_zero(engine):
    with engine.begin() as conn:
        _insert(conn, "developers", {"name": "Example Developer"})
        _insert(conn, "listings", LISTING)
        _insert(conn, "payment_plans", {"plan_id": "p_unknown", "listing_id": "lst_test_1",
                                        "years": 8, "frequency": "quarterly"})
        _insert(conn, "payment_plans", {"plan_id": "p_zero", "listing_id": "lst_test_1",
                                        "down_payment_egp": 0, "down_payment_pct": 0,
                                        "down_payment_source": "pct", "years": 10,
                                        "frequency": "monthly", "delivery_payment_pct": 0})
        rows = {r.plan_id: r for r in conn.execute(sa.text("SELECT * FROM payment_plans"))}
        listing = conn.execute(sa.text("SELECT * FROM listings")).one()
        conn.execute(sa.text("DELETE FROM payment_plans; DELETE FROM listings;"
                             " DELETE FROM developers"))
    assert rows["p_unknown"].down_payment_egp is None
    assert rows["p_unknown"].delivery_payment_pct is None
    assert rows["p_unknown"].delivery_month is None
    assert rows["p_zero"].down_payment_pct == 0
    assert rows["p_zero"].delivery_payment_pct == 0
    assert listing.delivery_payment_pct is None
    assert listing.missing_fields == []
    assert listing.data_version is None


@live
@pytest.mark.parametrize(
    ("table", "bad"),
    [
        ("listings", {"price_egp": 0}),
        ("listings", {"frequency": "yearly"}),
        ("listings", {"developer": "Unknown Developer"}),          # no such developer
        ("payment_plans", {"down_payment_source": "egp"}),          # egp source, no amount
        ("payment_plans", {"down_payment_egp": 100_000}),           # value without a source
        ("payment_plans", {"down_payment_pct": 80, "down_payment_source": "pct",
                           "delivery_payment_pct": 30}),            # more than 100 %
        ("payment_plans", {"delivery_month": -1}),
        ("payment_plans", {"listing_id": "lst_missing"}),
    ],
)
def test_live_bad_rows_rejected(engine, table, bad):
    plan = {"plan_id": "p_bad", "listing_id": "lst_test_1", "years": 5, "frequency": "monthly"}
    with pytest.raises(sa.exc.IntegrityError), engine.begin() as conn:
        _insert(conn, "developers", {"name": "Example Developer"})
        if table == "listings":
            _insert(conn, "listings", {**LISTING, **bad})
        else:
            _insert(conn, "listings", LISTING)
            _insert(conn, "payment_plans", {**plan, **bad})
