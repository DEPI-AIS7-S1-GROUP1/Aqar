"""S2: tests for developer_schedule(), mortgage_schedule(), build_plan().

Expected values are worked out by hand in the comments (README conventions), not by the code.
"""

import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.contracts import Listing, PaymentPlan, PlanResult
from app.finance.calculator import plan_npv
from app.finance.schedule import (
    PlanNotComputable,
    build_plan,
    developer_schedule,
    months_between,
    mortgage_amortization,
    mortgage_schedule,
    pmt,
)

EGP = 0.01


def plan(**kw) -> PaymentPlan:
    base = {
        "plan_id": "P-1",
        "down_payment_pct": 10.0,
        "down_payment_source": "pct",
        "years": 8,
        "frequency": "quarterly",
        "delivery_payment_pct": 10.0,
        "delivery_month": 36,
    }
    base.update(kw)
    return PaymentPlan(**base)


def rows(result: PlanResult, kind: str):
    return [p for p in result.payments if p.type == kind]


# ---------------- developer plans ----------------

def test_quarterly_with_delivery():
    # price 4,800,000: down 10% = 480,000 (month 0), delivery 10% = 480,000 (month 36)
    # remaining 3,840,000 over 8 years x 4 = 32 installments -> 120,000 each, 40,000 a month
    r = developer_schedule(plan(), listing_id="L1", price_egp=4_800_000)
    assert r.down_payment_egp == pytest.approx(480_000, abs=EGP)
    assert r.delivery_payment_egp == pytest.approx(480_000, abs=EGP)
    assert r.installment_count == 32
    assert r.installment_egp == pytest.approx(120_000, abs=EGP)
    assert r.monthly_equivalent_egp == pytest.approx(40_000, abs=EGP)
    assert r.total_paid_egp == pytest.approx(4_800_000, abs=EGP)
    assert [p.month for p in rows(r, "installment")][:3] == [3, 6, 9]
    assert rows(r, "installment")[-1].month == 96
    (d,) = rows(r, "delivery")
    assert d.month == 36
    assert len(r.payments) == 1 + 32 + 1
    assert r.warnings == [] and r.missing_fields == []


def test_monthly_no_delivery_real_zero():
    # price 3,000,000, down 5% = 150,000, delivery 0% (a real zero), 8 years monthly = 96
    # 2,850,000 / 96 = 29,687.50 (no rounding)
    r = developer_schedule(
        plan(down_payment_pct=5.0, frequency="monthly", delivery_payment_pct=0.0, delivery_month=None),
        listing_id="L2",
        price_egp=3_000_000,
    )
    assert r.installment_egp == pytest.approx(29_687.5, abs=EGP)
    assert r.monthly_equivalent_egp == r.installment_egp
    assert [p.month for p in rows(r, "installment")][:3] == [1, 2, 3]
    assert rows(r, "delivery") == []
    assert r.delivery_payment_egp == 0.0
    assert r.delivery_month is None


def test_zero_down_is_a_real_zero():
    # 3,600,000 over 10 years monthly, 0% down: 120 x 30,000; the month-0 row exists with 0
    r = developer_schedule(
        plan(down_payment_pct=0.0, years=10, frequency="monthly", delivery_payment_pct=0.0, delivery_month=None),
        listing_id="L3",
        price_egp=3_600_000,
    )
    (down,) = rows(r, "down_payment")
    assert down.month == 0 and down.amount_egp == 0.0
    assert r.installment_egp == pytest.approx(30_000, abs=EGP)


def test_full_down_payment():
    # 100% down: everything in month 0, no installments, NPV = price at any rate
    r = developer_schedule(
        plan(down_payment_pct=100.0, years=15, frequency="monthly", delivery_payment_pct=0.0, delivery_month=None),
        listing_id="L4",
        price_egp=2_000_000,
    )
    assert r.installment_count == 0
    assert r.installment_egp == 0.0
    assert len(r.payments) == 1
    assert plan_npv(r, 20.0).npv_egp == pytest.approx(2_000_000, abs=EGP)


def test_delivery_unknown_stays_unknown():
    r = developer_schedule(plan(delivery_payment_pct=None, delivery_month=None), listing_id="L5", price_egp=4_800_000)
    assert r.delivery_payment_egp is None
    assert r.installment_egp is None and r.monthly_equivalent_egp is None
    assert r.payments is None
    assert "delivery_payment_unknown" in r.warnings
    assert "delivery_payment_egp" in r.missing_fields
    assert plan_npv(r, 20.0).npv_egp is None


def test_delivery_month_unknown_keeps_installment_but_no_table():
    # remaining is known (delivery % known), so the installment is known; only the table is not
    r = developer_schedule(plan(delivery_month=None), listing_id="L6", price_egp=4_800_000)
    assert r.installment_egp == pytest.approx(120_000, abs=EGP)
    assert r.payments is None
    assert "delivery_month_unknown" in r.warnings


def test_down_payment_in_egp():
    # source gave 500,000 EGP on a 5,000,000 unit -> 10%
    r = developer_schedule(
        plan(down_payment_egp=500_000, down_payment_pct=None, down_payment_source="egp"),
        listing_id="L7",
        price_egp=5_000_000,
    )
    assert r.down_payment_egp == 500_000
    assert r.down_payment_pct == pytest.approx(10.0)


def test_down_payment_unknown_cannot_be_computed():
    p = PaymentPlan(plan_id="P-x", years=8, frequency="monthly", delivery_payment_pct=0.0)
    with pytest.raises(PlanNotComputable) as e:
        developer_schedule(p, listing_id="L8", price_egp=1_000_000)
    assert "down_payment_pct" in e.value.missing_fields


def test_down_plus_delivery_above_price_is_rejected():
    p = plan(down_payment_egp=4_000_000, down_payment_pct=None, down_payment_source="egp", delivery_payment_pct=30.0)
    with pytest.raises(ValueError):
        developer_schedule(p, listing_id="L9", price_egp=5_000_000)


def test_delivery_in_an_installment_month_is_its_own_row():
    r = developer_schedule(plan(frequency="monthly", delivery_month=12), listing_id="L10", price_egp=4_800_000)
    month12 = [p for p in r.payments if p.month == 12]
    assert [p.type for p in month12] == ["installment", "delivery"]


def test_npv_at_zero_rate_equals_total_paid():
    r = developer_schedule(plan(), listing_id="L11", price_egp=4_800_000)
    assert plan_npv(r, 0.0).npv_egp == pytest.approx(4_800_000, abs=EGP)


# ---------------- bank loans ----------------

def test_pmt_matches_google_sheets():
    # =PMT(15%/12, 120, -4000000) = 64,533.98
    assert round(pmt(4_000_000, 15.0, 120), 2) == 64_533.98


def test_mortgage_schedule():
    r = mortgage_schedule(
        listing_id="L20", plan_id="BANK-1", price_egp=5_000_000,
        down_payment_egp=1_000_000, annual_interest_rate_pct=15.0, years=10,
    )
    assert r.plan_type == "bank"
    assert r.installment_count == 120
    assert round(r.installment_egp, 2) == 64_533.98
    assert r.total_paid_egp == pytest.approx(1_000_000 + r.installment_egp * 120, abs=EGP)
    assert r.down_payment_pct == pytest.approx(20.0)
    assert len(r.payments) == 121


def test_mortgage_zero_interest():
    # 1,200,000 loan at 0% over 10 years = 10,000 a month
    r = mortgage_schedule(
        listing_id="L21", plan_id="BANK-0", price_egp=1_500_000,
        down_payment_egp=300_000, annual_interest_rate_pct=0.0, years=10,
    )
    assert r.installment_egp == pytest.approx(10_000, abs=EGP)
    assert r.total_paid_egp == pytest.approx(1_500_000, abs=EGP)


def test_amortization_ends_at_zero():
    table = mortgage_amortization(4_000_000, 15.0, 10)
    assert len(table) == 120
    assert table[-1].balance_egp == pytest.approx(0, abs=EGP)
    assert sum(row.principal_egp for row in table) == pytest.approx(4_000_000, abs=EGP)
    # first month: interest = 4,000,000 x 1.25% = 50,000
    assert table[0].interest_egp == pytest.approx(50_000, abs=EGP)


# ---------------- listing -> plan ----------------

def listing(**kw) -> Listing:
    base = {
        "listing_id": "NC-101",
        "source_url": "https://example.invalid/x",
        "collected_at": datetime(2026, 11, 20, tzinfo=UTC),
        "collected_by": "t",
        "area": "new_cairo",
        "developer": "Demo",
        "price_egp": 4_800_000,
        "area_sqm": 145,
        "delivery_date": date(2029, 12, 1),
        "down_payment_pct": 10.0,
        "years": 8,
        "frequency": "quarterly",
        "delivery_payment_pct": 10.0,
    }
    base.update(kw)
    return Listing(**base)


def test_months_between():
    assert months_between(date(2026, 12, 1), date(2029, 12, 1)) == 36
    assert months_between(date(2026, 12, 1), date(2025, 1, 1)) == 0


def test_build_plan_counts_delivery_month_from_contract_date():
    r = build_plan(listing(), as_of=date(2026, 12, 1))
    assert r.delivery_month == 36
    assert r.plan_id == "P-NC-101"
    assert r.payments is not None


def test_build_plan_without_contract_date_keeps_month_unknown():
    r = build_plan(listing())
    assert r.payments is None
    assert "delivery_month_unknown" in r.warnings


def test_build_plan_with_rate_fills_npv():
    r = build_plan(listing(), as_of=date(2026, 12, 1), annual_discount_rate_pct=0.0)
    assert r.npv_egp == pytest.approx(4_800_000, abs=EGP)
    assert r.annual_discount_rate_pct == 0.0
    r20 = build_plan(listing(), as_of=date(2026, 12, 1), annual_discount_rate_pct=20.0)
    assert r20.npv_egp < 4_800_000
