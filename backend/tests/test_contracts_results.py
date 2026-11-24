"""S0-T3-4: tests for PlanResult, AffordabilityResult and the PaymentPlan changes.

Also re-checks models written by other members (Listing, AffordabilityEntry) so the
contract changes do not break them.
"""

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

BACKEND = Path(__file__).parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.contracts import (
    AffordabilityEntry,
    AffordabilityResult,
    LeadState,
    Listing,
    PaymentPlan,
    PlanResult,
)

EXAMPLES = Path(__file__).parent / "contract_examples"


def load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def plan_result(**overrides) -> PlanResult:
    data = load("planresult_example.json")
    data.update(overrides)
    return PlanResult(**data)


def affordability(**overrides) -> AffordabilityResult:
    data = load("affordabilityresult_example.json")
    data.update(overrides)
    return AffordabilityResult(**data)


UNKNOWN_MONTHLY = {
    "status": "unknown",
    "monthly_capacity_egp": None,
    "monthly_gap_egp": None,
    "missing_inputs": ["monthly_capacity_egp"],
}


# ---------- examples round-trip ----------

@pytest.mark.parametrize(
    ("model", "filename"),
    [
        (PlanResult, "planresult_example.json"),
        (AffordabilityResult, "affordabilityresult_example.json"),
        (PaymentPlan, "paymentplan_example.json"),
        (Listing, "listing_example.json"),
    ],
)
def test_example_round_trip(model, filename):
    data = load(filename)
    obj = model.model_validate(data)
    again = model.model_validate_json(obj.model_dump_json())
    assert again == obj


def test_listing_example_still_loads_without_listing_id():
    listing = Listing(**load("listing_example.json"))
    assert listing.listing_id is None
    assert listing.area == "القاهرة الجديدة"   # Arabic text survives as-is


# ---------- PaymentPlan: None vs 0 ----------

def test_payment_plan_required_fields_only_leaves_optionals_none():
    plan = PaymentPlan(plan_id="p1", years=8, frequency="quarterly")
    assert plan.down_payment_egp is None
    assert plan.down_payment_pct is None
    assert plan.down_payment_source is None
    assert plan.delivery_payment_pct is None
    assert plan.delivery_month is None
    assert plan.maintenance_pct is None


def test_zero_down_payment_stays_zero_not_none():
    plan = PaymentPlan(
        plan_id="p1", down_payment_egp=0.0, down_payment_source="egp",
        years=7, frequency="monthly",
    )
    assert plan.down_payment_egp == 0.0
    assert plan.down_payment_egp is not None
    assert plan.down_payment_pct is None   # not computed here


def test_amount_only_source():
    plan = PaymentPlan(
        plan_id="p1", down_payment_egp=150_000, down_payment_source="egp",
        years=10, frequency="monthly",
    )
    assert plan.down_payment_egp == 150_000.0
    assert plan.down_payment_pct is None


def test_percent_only_source():
    plan = PaymentPlan(
        plan_id="p1", down_payment_pct=10, down_payment_source="pct",
        years=10, frequency="monthly",
    )
    assert plan.down_payment_pct == 10.0
    assert plan.down_payment_egp is None


def test_amount_and_percent_both_allowed_reconciling_is_loader_job():
    plan = PaymentPlan(
        plan_id="p1", down_payment_egp=150_000, down_payment_pct=12.5,
        down_payment_source="egp", years=10, frequency="monthly",
    )
    assert plan.down_payment_egp == 150_000.0
    assert plan.down_payment_pct == 12.5


@pytest.mark.parametrize(
    "fields",
    [
        {"down_payment_source": "egp"},                       # says egp, no amount
        {"down_payment_source": "pct"},                       # says pct, no percent
        {"down_payment_pct": 10},                             # value without a source
        {"down_payment_egp": 100_000},
        {"down_payment_egp": -1, "down_payment_source": "egp"},  # negative amount
        {"down_payment_pct": 101, "down_payment_source": "pct"},
        {"down_payment_pct": -5, "down_payment_source": "pct"},
        {"down_payment_pct": 95, "down_payment_source": "pct", "delivery_payment_pct": 10},
        {"delivery_month": -1},
    ],
)
def test_payment_plan_rejects_bad_down_payment(fields):
    with pytest.raises(ValidationError):
        PaymentPlan(plan_id="p1", years=10, frequency="monthly", **fields)


def test_payment_plan_rejects_negative_years():
    with pytest.raises(ValidationError):
        PaymentPlan(plan_id="p1", years=-1, frequency="monthly")


def test_payment_plan_needs_plan_id():
    with pytest.raises(ValidationError):
        PaymentPlan(years=10, frequency="monthly")


@pytest.mark.parametrize("raw", ["١٠", "١٠٪", "٥٠٠٬٠٠٠"])
def test_arabic_indic_digits_are_not_parsed_by_contracts(raw):
    # Normalising Arabic-Indic digits belongs to validate_fixtures.py / S1-T10-2.
    with pytest.raises(ValidationError):
        PaymentPlan(
            plan_id="p1", down_payment_pct=raw, down_payment_source="pct",
            years=10, frequency="monthly",
        )


# ---------- PlanResult ----------

def test_plan_result_optional_fields_default_to_none():
    r = PlanResult(
        listing_id="l1", plan_id="p1", plan_type="bank", price_egp=1_000_000,
        down_payment_egp=200_000, down_payment_pct=20, installment_count=60,
        installment_egp=20_000, monthly_equivalent_egp=20_000, total_paid_egp=1_400_000,
    )
    assert r.delivery_payment_egp is None
    assert r.delivery_month is None
    assert r.npv_egp is None
    assert r.annual_discount_rate_pct is None
    assert r.warnings == []          # bank plans have no delivery payment


def test_unknown_delivery_payment_stays_none_with_warning():
    r = plan_result(delivery_payment_egp=None, delivery_month=None)
    assert r.delivery_payment_egp is None
    assert r.warnings == ["delivery_payment_unknown"]


def test_unknown_delivery_warning_not_duplicated():
    r = plan_result(delivery_payment_egp=None, warnings=["delivery_payment_unknown"])
    assert r.warnings.count("delivery_payment_unknown") == 1


def test_zero_delivery_payment_is_real_zero_no_warning():
    r = plan_result(delivery_payment_egp=0.0, delivery_month=None)
    assert r.delivery_payment_egp == 0.0
    assert r.warnings == []


def test_delivery_payment_without_month_warns():
    r = plan_result(delivery_month=None)
    assert "delivery_month_unknown" in r.warnings


def test_zero_down_payment_plan():
    r = plan_result(
        down_payment_egp=0.0, down_payment_pct=0.0, delivery_payment_egp=0.0,
        installment_count=120, installment_egp=20_000, monthly_equivalent_egp=20_000,
    )
    assert r.down_payment_egp == 0.0
    assert r.down_payment_pct == 0.0


def test_full_down_payment_plan():
    r = plan_result(
        down_payment_egp=2_400_000, down_payment_pct=100, delivery_payment_egp=0.0,
        delivery_month=None, installment_count=0, installment_egp=0.0,
        monthly_equivalent_egp=0.0, npv_egp=2_400_000, annual_discount_rate_pct=20,
    )
    assert r.installment_egp == 0.0
    assert r.npv_egp == r.price_egp


@pytest.mark.parametrize(
    "fields",
    [
        {"down_payment_egp": -1},
        {"installment_egp": -1},
        {"total_paid_egp": -1},
        {"price_egp": 0},
        {"down_payment_pct": 120},
        {"down_payment_egp": 2_300_000},                    # down + delivery > price
        {"installment_count": 0},                           # 1.92M left, no installments
        {"installment_count": 0, "installment_egp": 0.0,
         "monthly_equivalent_egp": 0.0},                     # still 1.92M unpaid
        {"npv_egp": 2_000_000},                             # npv without its rate
        {"annual_discount_rate_pct": 20},                   # rate without npv
        {"plan_type": "crypto"},
    ],
)
def test_plan_result_rejects_bad_values(fields):
    with pytest.raises(ValidationError):
        plan_result(**fields)


# ---------- AffordabilityResult ----------

def test_affordability_unknown_with_missing_inputs():
    r = affordability(**UNKNOWN_MONTHLY)
    assert r.status == "unknown"
    assert r.monthly_capacity_egp is None
    assert r.monthly_gap_egp is None


def test_affordability_unknown_needs_missing_inputs():
    with pytest.raises(ValidationError):
        affordability(**{**UNKNOWN_MONTHLY, "missing_inputs": []})


@pytest.mark.parametrize("status", ["fit", "tight", "not_fit"])
def test_known_status_needs_both_gaps(status):
    with pytest.raises(ValidationError):
        affordability(status=status, monthly_capacity_egp=None, monthly_gap_egp=None)


def test_known_status_cannot_have_missing_inputs():
    with pytest.raises(ValidationError):
        affordability(status="fit", missing_inputs=["timeline"])


def test_gap_must_match_required_minus_available():
    with pytest.raises(ValidationError):
        affordability(monthly_gap_egp=5_000)


def test_gap_without_inputs_rejected():
    with pytest.raises(ValidationError):
        affordability(status="unknown", monthly_capacity_egp=None,
                      missing_inputs=["monthly_capacity_egp"])


def test_zero_down_available_is_real_zero():
    r = affordability(down_payment_available_egp=0.0, down_payment_gap_egp=240_000.0,
                      status="not_fit")
    assert r.down_payment_available_egp == 0.0
    assert r.down_payment_gap_egp == 240_000.0


def test_negative_amounts_rejected():
    with pytest.raises(ValidationError):
        affordability(monthly_capacity_egp=-1, monthly_gap_egp=20_001)


def test_to_entry_returns_affordability_entry():
    r = affordability()
    entry = r.to_entry()
    assert isinstance(entry, AffordabilityEntry)
    assert entry.model_dump() == {
        "listing_id": "lst_example_001",
        "plan_id": "plan_001",
        "status": "tight",
        "flags": ["delivery_payment"],
    }
    entry.flags.append("x")
    assert r.flags == ["delivery_payment"]   # copy, not shared


def test_to_entry_fits_on_lead_state():
    entry = affordability(**UNKNOWN_MONTHLY).to_entry()
    lead = LeadState(conversation_id="c1", lead_id="lead1", affordability=[entry])
    assert lead.affordability[0].status == "unknown"


def test_affordability_entry_unchanged():
    entry = AffordabilityEntry(listing_id="l1", plan_id="p1", status="fit")
    assert entry.flags == []
