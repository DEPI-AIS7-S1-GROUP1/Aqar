"""S2: tests for check_affordability().

Plan used: price 4,800,000, down 480,000, delivery 480,000 in month 36,
quarterly 120,000 = 40,000 a month (see test_schedule.py).
"""

import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.contracts import PaymentPlan, Slots
from app.finance.affordability import (
    FLAG_DELIVERY,
    FLAG_MONTHLY_SHORT,
    check_affordability,
    check_affordability_for_slots,
    load_config,
)
from app.finance.schedule import developer_schedule

EGP = 0.01


@pytest.fixture
def plan():
    return developer_schedule(
        PaymentPlan(
            plan_id="P-1", down_payment_pct=10.0, down_payment_source="pct", years=8,
            frequency="quarterly", delivery_payment_pct=10.0, delivery_month=36,
        ),
        listing_id="L1",
        price_egp=4_800_000,
    )


def test_config_limit_is_15_pct():
    assert load_config()["tight_limit_pct"] == 15


def test_fit_when_everything_is_covered(plan):
    # 1,000,000 - 480,000 = 520,000 left, which covers the 480,000 delivery payment
    r = check_affordability(plan, 1_000_000, 50_000)
    assert r.status == "fit"
    assert r.down_payment_gap_egp == pytest.approx(-520_000, abs=EGP)
    assert r.monthly_gap_egp == pytest.approx(-10_000, abs=EGP)
    assert r.flags == []


def test_tight_when_delivery_not_covered(plan):
    # 500,000 - 480,000 = 20,000 left, less than the 480,000 delivery payment
    r = check_affordability(plan, 500_000, 45_000)
    assert r.status == "tight"
    assert FLAG_DELIVERY in r.flags


def test_tight_at_exactly_15_pct_over(plan):
    # 40,000 / 1.15 = 34,782.61 -> the installment is exactly 15% above the capacity
    r = check_affordability(plan, 1_000_000, 40_000 / 1.15)
    assert r.status == "tight"
    assert FLAG_MONTHLY_SHORT in r.flags


def test_not_fit_above_15_pct(plan):
    # 40,000 / 34,000 - 1 = 17.6% over
    assert check_affordability(plan, 1_000_000, 34_000).status == "not_fit"


def test_not_fit_with_delivery_note(plan):
    # 480,000 / 300,000 - 1 = 60% over on the down payment, delivery not covered either
    r = check_affordability(plan, 300_000, 20_000)
    assert r.status == "not_fit"
    assert FLAG_DELIVERY in r.flags
    assert "دفعة الاستلام" in r.reason


def test_unknown_customer_input(plan):
    r = check_affordability(plan, 600_000, None)
    assert r.status == "unknown"
    assert r.missing_fields == ["monthly_capacity_egp"]
    assert r.monthly_gap_egp is None
    assert r.down_payment_gap_egp == pytest.approx(-120_000, abs=EGP)


def test_unknown_when_plan_installment_unknown():
    p = developer_schedule(
        PaymentPlan(plan_id="P-2", down_payment_pct=10.0, down_payment_source="pct", years=8, frequency="monthly"),
        listing_id="L2",
        price_egp=3_000_000,
    )
    r = check_affordability(p, 1_000_000, 50_000)
    assert r.status == "unknown"
    assert "monthly_required_egp" in r.missing_fields


def test_reasons_have_no_digits(plan):
    for args in [(1_000_000, 50_000), (500_000, 45_000), (300_000, 20_000), (None, None)]:
        r = check_affordability(plan, *args)
        assert not any(ch.isdigit() for ch in r.reason)


def test_only_confirmed_slots_count(plan):
    s = Slots()
    s.down_payment_available_egp.value = 1_000_000
    s.monthly_capacity_egp.value = 50_000
    assert check_affordability_for_slots(plan, s).status == "unknown"
    s.down_payment_available_egp.confirmed = True
    s.monthly_capacity_egp.confirmed = True
    assert check_affordability_for_slots(plan, s).status == "fit"


def test_entry_for_lead_state(plan):
    e = check_affordability(plan, 500_000, 45_000).to_entry()
    assert e.status == "tight" and e.flags == [FLAG_DELIVERY]
