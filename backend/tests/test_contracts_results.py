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
    Payment,
    PaymentPlan,
    PlanResult,
)

EXAMPLES = Path(__file__).parent / "contract_examples"


def load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def plan_result(**overrides) -> PlanResult:
    """The example without its payment table, so one-field overrides stay valid.

    Pass ``payments=...`` to test the table itself.
    """
    data = load("planresult_example.json")
    data.pop("payments")
    data.update(overrides)
    return PlanResult(**data)


def example_payments() -> list[dict]:
    return load("planresult_example.json")["payments"]


def affordability(**overrides) -> AffordabilityResult:
    data = load("affordabilityresult_example.json")
    data.update(overrides)
    return AffordabilityResult(**data)


UNKNOWN_MONTHLY = {
    "status": "unknown",
    "monthly_capacity_egp": None,
    "monthly_gap_egp": None,
    "missing_fields": ["monthly_capacity_egp"],
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


# ---------- PlanResult.payments (the payment table) ----------

def test_example_payment_table_matches_totals():
    r = PlanResult(**load("planresult_example.json"))
    assert r.payments is not None
    assert [p.type for p in r.payments].count("installment") == r.installment_count
    assert sum(p.amount_egp for p in r.payments) == r.total_paid_egp
    assert r.payments[0] == Payment(month=0, amount_egp=240_000, type="down_payment")


def test_payments_default_to_none_meaning_unknown():
    r = plan_result()
    assert r.payments is None


def test_unknown_delivery_payment_means_no_payment_table():
    # Unknown delivery: the table cannot be built, and it must not be built as if it were 0.
    with pytest.raises(ValidationError, match="delivery_payment_egp is unknown"):
        plan_result(delivery_payment_egp=None, delivery_month=None, payments=example_payments())


def test_unknown_delivery_month_means_no_payment_table():
    with pytest.raises(ValidationError, match="delivery_month is unknown"):
        plan_result(delivery_month=None, payments=example_payments())


def test_bank_plan_without_delivery_can_have_a_table():
    pays = [{"month": 0, "amount_egp": 200_000, "type": "down_payment"}]
    pays += [{"month": m, "amount_egp": 20_000, "type": "installment"} for m in range(1, 61)]
    r = PlanResult(
        listing_id="l1", plan_id="p1", plan_type="bank", price_egp=1_000_000,
        down_payment_egp=200_000, down_payment_pct=20, installment_count=60,
        installment_egp=20_000, monthly_equivalent_egp=20_000, total_paid_egp=1_400_000,
        payments=pays,
    )
    assert len(r.payments) == 61


def test_zero_down_payment_row_is_a_real_zero():
    pays = [{"month": 0, "amount_egp": 0.0, "type": "down_payment"}]
    pays += [{"month": m, "amount_egp": 20_000, "type": "installment"} for m in range(1, 121)]
    r = plan_result(
        down_payment_egp=0.0, down_payment_pct=0.0, delivery_payment_egp=0.0,
        installment_count=120, installment_egp=20_000, monthly_equivalent_egp=20_000,
        payments=pays,
    )
    assert r.payments[0].amount_egp == 0.0


def test_full_down_payment_table_has_one_row():
    r = plan_result(
        down_payment_egp=2_400_000, down_payment_pct=100, delivery_payment_egp=0.0,
        delivery_month=None, installment_count=0, installment_egp=0.0,
        monthly_equivalent_egp=0.0,
        payments=[{"month": 0, "amount_egp": 2_400_000, "type": "down_payment"}],
    )
    assert len(r.payments) == 1


def test_maintenance_row_is_not_part_of_total_paid():
    pays = example_payments()
    pays.append({"month": 36, "amount_egp": 192_000, "type": "maintenance"})
    pays.sort(key=lambda p: p["month"])
    r = plan_result(payments=pays)
    assert r.total_paid_egp == 2_400_000


def _broken(change) -> list[dict]:
    pays = example_payments()
    change(pays)
    return pays


@pytest.mark.parametrize(
    "pays",
    [
        [],                                                              # empty is not unknown
        _broken(lambda p: p.pop(0)),                                     # no down payment row
        _broken(lambda p: p.insert(0, dict(p[0]))),                      # two down payment rows
        _broken(lambda p: p[0].update(month=1)),                         # down payment not month 0
        _broken(lambda p: p[0].update(amount_egp=1.0)),                  # wrong down amount
        _broken(lambda p: p.pop(1)),                                     # one installment missing
        _broken(lambda p: p[1].update(amount_egp=59_000)),               # wrong installment
        _broken(lambda p: p.pop(next(i for i, x in enumerate(p)
                                     if x["type"] == "delivery"))),     # no delivery row
        _broken(lambda p: next(x for x in p
                               if x["type"] == "delivery").update(month=48)),  # wrong month
        _broken(lambda p: p.reverse()),                                  # not sorted
        _broken(lambda p: p[0].update(amount_egp=-1)),                   # negative amount
        _broken(lambda p: p[0].update(amount_egp=float("nan"))),         # NaN amount
        _broken(lambda p: p[0].update(type="bonus")),                    # unknown type
    ],
)
def test_bad_payment_table_rejected(pays):
    with pytest.raises(ValidationError):
        plan_result(payments=pays)


def test_delivery_row_rejected_when_plan_has_no_delivery():
    pays = [{"month": 0, "amount_egp": 0.0, "type": "down_payment"},
            {"month": 1, "amount_egp": 1_000_000, "type": "installment"},
            {"month": 2, "amount_egp": 0.0, "type": "delivery"}]
    with pytest.raises(ValidationError, match="no delivery payment"):
        PlanResult(
            listing_id="l1", plan_id="p1", plan_type="developer", price_egp=1_000_000,
            down_payment_egp=0, down_payment_pct=0, delivery_payment_egp=0.0,
            installment_count=1, installment_egp=1_000_000,
            monthly_equivalent_egp=1_000_000, total_paid_egp=1_000_000, payments=pays,
        )


# ---------- AffordabilityResult ----------

def test_affordability_unknown_with_missing_fields():
    r = affordability(**UNKNOWN_MONTHLY)
    assert r.status == "unknown"
    assert r.monthly_capacity_egp is None
    assert r.monthly_gap_egp is None


def test_affordability_unknown_needs_missing_fields():
    with pytest.raises(ValidationError):
        affordability(**{**UNKNOWN_MONTHLY, "missing_fields": []})


@pytest.mark.parametrize("status", ["fit", "tight", "not_fit"])
def test_known_status_needs_both_gaps(status):
    with pytest.raises(ValidationError):
        affordability(status=status, monthly_capacity_egp=None, monthly_gap_egp=None)


def test_known_status_cannot_have_missing_fields():
    with pytest.raises(ValidationError):
        affordability(status="fit", missing_fields=["timeline"])


def test_gap_must_match_required_minus_available():
    with pytest.raises(ValidationError):
        affordability(monthly_gap_egp=5_000)


def test_gap_without_inputs_rejected():
    with pytest.raises(ValidationError):
        affordability(status="unknown", monthly_capacity_egp=None,
                      missing_fields=["monthly_capacity_egp"])


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


# ---------- S0-T3-4 sheet alignment: missing_fields and reason ----------

def test_plan_result_missing_fields_empty_when_everything_known():
    assert plan_result().missing_fields == []


def test_unknown_delivery_payment_listed_in_missing_fields():
    r = plan_result(delivery_payment_egp=None, delivery_month=None)
    assert r.missing_fields == ["delivery_payment_egp"]
    assert r.delivery_payment_egp is None          # still None, never 0


def test_unknown_delivery_month_listed_in_missing_fields():
    r = plan_result(delivery_month=None)
    assert r.missing_fields == ["delivery_month"]


def test_zero_delivery_payment_is_not_missing():
    r = plan_result(delivery_payment_egp=0.0, delivery_month=None)
    assert r.missing_fields == []


def test_bank_plan_without_delivery_is_not_missing():
    r = PlanResult(
        listing_id="l1", plan_id="p1", plan_type="bank", price_egp=1_000_000,
        down_payment_egp=200_000, down_payment_pct=20, installment_count=60,
        installment_egp=20_000, monthly_equivalent_egp=20_000, total_paid_egp=1_400_000,
    )
    assert r.missing_fields == []


def test_missing_fields_keeps_caller_entries_and_is_not_duplicated():
    r = plan_result(delivery_payment_egp=None,
                    missing_fields=["maintenance_pct", "delivery_payment_egp"])
    assert r.missing_fields == ["maintenance_pct", "delivery_payment_egp"]


def test_affordability_reason_is_required():
    data = load("affordabilityresult_example.json")
    data.pop("reason")
    with pytest.raises(ValidationError):
        AffordabilityResult(**data)


@pytest.mark.parametrize("reason", ["", "   "])
def test_affordability_reason_cannot_be_blank(reason):
    with pytest.raises(ValidationError):
        affordability(reason=reason)


@pytest.mark.parametrize(
    "reason",
    [
        "Monthly installment is 2000 EGP above capacity.",
        "القسط أعلى من قدرتك بـ ٢٠٠٠ جنيه",        # Arabic-Indic digits
        "Down payment short by 5%",
    ],
)
def test_affordability_reason_cannot_carry_numbers(reason):
    with pytest.raises(ValidationError, match="must not contain numbers"):
        affordability(reason=reason)


def test_affordability_reason_accepts_arabic_text():
    reason = "المقدم متغطي، بس القسط الشهري أعلى من القدرة."
    assert affordability(reason=reason).reason == reason


def test_affordability_has_exactly_four_states():
    import typing

    from app.contracts import AffordabilityStatus
    assert set(typing.get_args(AffordabilityStatus)) == {"fit", "tight", "not_fit", "unknown"}
    with pytest.raises(ValidationError):
        affordability(status="comfortable")


def test_old_missing_inputs_name_is_not_a_field():
    # The old field name must not be accepted as a stand-in for missing_fields.
    r = affordability(**{**UNKNOWN_MONTHLY, "missing_fields": ["monthly_capacity_egp"],
                         "missing_inputs": ["x"]})
    assert r.missing_fields == ["monthly_capacity_egp"]
    assert not hasattr(r, "missing_inputs")
