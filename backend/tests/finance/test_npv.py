"""S1-T3-3: tests for npv(), plan_cashflows() and plan_npv().

Convention A (docs/calculator-reference/README.md):
    monthly_rate = (1 + annual)^(1/12) - 1, DF_t = 1 / (1 + monthly_rate)^t = (1 + annual)^(-t/12)
So a payment in month 12 at 25 % is worth amount / 1.25, and month 0 is never discounted.

Expected values below are worked out by hand in the comments; the code is not used to
produce them.
"""

import itertools
import json
import math
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.contracts import PlanResult
from app.finance.calculator import (
    WARNING_NPV_DELIVERY_MONTH_UNKNOWN,
    WARNING_NPV_DELIVERY_UNKNOWN,
    WARNING_NPV_PAYMENTS_UNKNOWN,
    monthly_rate,
    npv,
    plan_cashflows,
    plan_npv,
)

EXAMPLES = BACKEND / "tests" / "contract_examples"


def example_plan() -> PlanResult:
    """Shared fixture: 2.4M, 10 % down, 10 % delivery at month 36, 32 quarterly x 60,000."""
    data = json.loads((EXAMPLES / "planresult_example.json").read_text(encoding="utf-8"))
    return PlanResult.model_validate(data)


def table(down: float, installment: float, count: int, step: int,
          delivery: float | None = None, delivery_month: int | None = None) -> list[dict]:
    """A payment table written by hand for the tests (npv() must not build it)."""
    rows = [{"month": 0, "amount_egp": down, "type": "down_payment"}]
    rows += [{"month": k * step, "amount_egp": installment, "type": "installment"}
             for k in range(1, count + 1)]
    if delivery:
        rows.append({"month": delivery_month, "amount_egp": delivery, "type": "delivery"})
    return sorted(rows, key=lambda r: r["month"])   # stable: delivery stays after its installment


def dev_plan(step: int = 3, **overrides) -> PlanResult:
    """Developer plan with its payment table. ``step`` = months between installments.

    The table is left out (``payments=None``) when it cannot be known: the delivery payment,
    or its month, is not published.
    """
    base = {
        "listing_id": "lst_t",
        "plan_id": "plan_t",
        "plan_type": "developer",
        "price_egp": 1_000_000.0,
        "down_payment_egp": 200_000.0,
        "down_payment_pct": 20.0,
        "delivery_payment_egp": 0.0,  # a real zero: this plan has no delivery payment
        "delivery_month": None,
        "installment_count": 4,
        "installment_egp": 200_000.0,
        "monthly_equivalent_egp": 200_000.0 / 3,  # quarterly
        "total_paid_egp": 1_000_000.0,
    }
    base.update(overrides)
    delivery, month = base["delivery_payment_egp"], base["delivery_month"]
    known = delivery is not None and (delivery == 0 or month is not None)
    if "payments" not in base and known:
        base["payments"] = table(base["down_payment_egp"], base["installment_egp"],
                                 base["installment_count"], step, delivery, month)
    return PlanResult(**base)


def bank_plan(price: float, down_pct: float, annual_rate_pct: float, years: int) -> PlanResult:
    """Bank plan built with the README PMT formula (written by Member 2, not by npv())."""
    down = price * down_pct / 100
    loan = price - down
    i = annual_rate_pct / 100 / 12
    n = years * 12
    pmt = loan * i / (1 - (1 + i) ** -n)
    return PlanResult(
        listing_id="lst_b",
        plan_id="plan_b",
        plan_type="bank",
        price_egp=price,
        down_payment_egp=down,
        down_payment_pct=down_pct,
        installment_count=n,
        installment_egp=pmt,
        monthly_equivalent_egp=pmt,
        total_paid_egp=down + pmt * n,
        payments=table(down, pmt, n, 1),
    )


def dense(flows: list[tuple[int, float]]) -> list[float]:
    """(month, amount) pairs -> one value per month, index = month (numpy-financial format)."""
    out = [0.0] * (max(m for m, _ in flows) + 1)
    for m, a in flows:
        out[m] += a
    return out


# ---- DoD 1: NPV at 0 % equals total nominal payments (first test, as the task asks) ----

def test_zero_rate_equals_total_paid_example_plan():
    # 240,000 + 32 x 60,000 + 240,000 = 2,400,000 (all exact in float)
    plan = example_plan()
    assert npv(plan_cashflows(plan), 0.0) == 2_400_000.0
    assert plan_npv(plan, 0.0).npv_egp == plan.total_paid_egp


def test_zero_rate_equals_total_paid_bank_plan():
    plan = bank_plan(2_000_000.0, 20.0, 18.0, 10)
    assert npv(plan_cashflows(plan), 0) == pytest.approx(plan.total_paid_egp, rel=1e-12)


def test_monthly_rate_zero_is_zero():
    assert monthly_rate(0.0) == 0.0


# ---- convention A, hand-computed values ----

def test_monthly_rate_compounds_back_to_annual():
    # (1 + m)^12 must give back 1.25 for 25 %
    assert (1 + monthly_rate(25.0)) ** 12 == pytest.approx(1.25, rel=1e-12)


def test_month_zero_is_not_discounted():
    assert npv([(0, 123_456.78)], 99.0) == 123_456.78


def test_npv_hand_computed_yearly_points():
    # 25 %: DF_12 = 1/1.25 = 0.8, DF_24 = 1/1.25^2 = 0.64
    # 100,000 + 80,000 + 64,000 = 244,000
    flows = [(0, 100_000.0), (12, 100_000.0), (24, 100_000.0)]
    assert npv(flows, 25.0) == pytest.approx(244_000.0, abs=1e-6)


def test_npv_hand_computed_half_year():
    # 21 %: DF_6 = 1.21^(-6/12) = 1/1.1 -> 110,000 / 1.1 = 100,000
    assert npv([(6, 110_000.0)], 21.0) == pytest.approx(100_000.0, abs=1e-6)


def test_same_month_payments_add_up():
    # two payments in month 12 at 25 %: (50,000 + 50,000) / 1.25 = 80,000
    assert npv([(12, 50_000.0), (12, 50_000.0)], 25.0) == pytest.approx(80_000.0, abs=1e-6)


def test_quarterly_plan_hand_computed():
    # 46.41 %: 1.4641^(1/4) = 1.1, so quarter k has DF = 1/1.1^k.
    # 200,000 down + 200,000 x (1/1.1 + 1/1.21 + 1/1.331 + 1/1.4641)
    # = 200,000 + 200,000 x 3.16986544635 = 833,973.09
    plan = dev_plan()
    assert plan_cashflows(plan) == [
        (0, 200_000.0), (3, 200_000.0), (6, 200_000.0), (9, 200_000.0), (12, 200_000.0)
    ]
    assert plan_npv(plan, 46.41).npv_egp == pytest.approx(833_973.09, abs=0.01)


# ---- DoD 2: higher rate gives lower NPV ----

@pytest.mark.parametrize("plan", [example_plan(), bank_plan(3_000_000.0, 10.0, 22.0, 7)])
def test_higher_rate_lower_npv(plan):
    flows = plan_cashflows(plan)
    values = [npv(flows, r) for r in (0, 5, 10, 20, 30, 50)]
    assert all(a > b for a, b in itertools.pairwise(values))


# ---- DoD 3: matches numpy-financial on the sample plans ----

@pytest.mark.parametrize("rate", [0.0, 12.0, 20.0, 27.25])
@pytest.mark.parametrize("plan", [example_plan(), bank_plan(3_000_000.0, 10.0, 22.0, 7)])
def test_matches_numpy_financial(plan, rate):
    npf = pytest.importorskip("numpy_financial")
    flows = plan_cashflows(plan)
    # numpy_financial.npv treats values[0] as time 0 (undiscounted), same as Convention A.
    expected = float(npf.npv(monthly_rate(rate), dense(flows)))
    assert npv(flows, rate) == pytest.approx(expected, rel=1e-12)


def test_example_plan_at_20_pct_value():
    # Recorded for the PR (also equal to numpy_financial.npv on the same flows):
    # m = 1.2^(1/12) - 1 = 0.0153094705; NPV = 1,366,254.17
    assert npv(plan_cashflows(example_plan()), 20.0) == pytest.approx(1_366_254.17, abs=0.01)


# ---- cash-flow building ----

def test_example_plan_cashflows():
    flows = plan_cashflows(example_plan())
    assert flows[0] == (0, 240_000.0)
    installments = [f for f in flows[1:] if f[1] == 60_000.0]
    assert [m for m, _ in installments] == list(range(3, 97, 3))  # months 3..96
    assert (36, 240_000.0) in flows  # delivery payment, same month as an installment
    assert sum(a for _, a in flows) == 2_400_000.0


def test_zero_down_plan():
    # 0 % down is a real 0: month 0 holds 0.0, 12 monthly x 10,000
    plan = dev_plan(
        step=1,
        price_egp=120_000.0, down_payment_egp=0.0, down_payment_pct=0.0,
        installment_count=12, installment_egp=10_000.0, monthly_equivalent_egp=10_000.0,
        total_paid_egp=120_000.0,
    )
    flows = plan_cashflows(plan)
    assert flows[0] == (0, 0.0)
    assert [m for m, _ in flows[1:]] == list(range(1, 13))
    assert plan_npv(plan, 0.0).npv_egp == 120_000.0
    assert plan_npv(plan, 20.0).npv_egp < 120_000.0


def test_full_down_payment_npv_equals_price_at_any_rate():
    # README cases 20, 21: 100 % down, installment 0, NPV = price (month 0 only)
    plan = dev_plan(
        down_payment_egp=1_000_000.0, down_payment_pct=100.0,
        installment_count=0, installment_egp=0.0, monthly_equivalent_egp=0.0,
    )
    assert plan_cashflows(plan) == [(0, 1_000_000.0)]
    for rate in (0.0, 15.0, 30.0):
        assert plan_npv(plan, rate).npv_egp == 1_000_000.0


def test_bank_plan_npv_at_loan_rate_equals_price():
    # Cross-check of the README bank PMT formula against Convention A:
    # discounting the PMTs at the loan's own effective rate gives back the loan, so
    # NPV = down + loan = price. Effective annual = (1 + 0.18/12)^12 - 1.
    plan = bank_plan(2_000_000.0, 20.0, 18.0, 10)
    effective_pct = ((1 + 0.18 / 12) ** 12 - 1) * 100
    assert plan_npv(plan, effective_pct).npv_egp == pytest.approx(2_000_000.0, abs=0.01)


# ---- unknown stays None, never 0 ----

def test_unknown_delivery_payment_gives_none_not_zero():
    plan = dev_plan(delivery_payment_egp=None)
    assert "delivery_payment_unknown" in plan.warnings  # added by the contract
    assert plan_cashflows(plan) is None
    result = plan_npv(plan, 20.0)
    assert result.npv_egp is None
    assert result.annual_discount_rate_pct is None
    assert WARNING_NPV_DELIVERY_UNKNOWN in result.warnings


def test_unknown_delivery_month_gives_none():
    plan = dev_plan(
        delivery_payment_egp=100_000.0, delivery_month=None,
        installment_count=4, installment_egp=175_000.0, monthly_equivalent_egp=175_000.0 / 3,
    )
    assert plan_cashflows(plan) is None
    result = plan_npv(plan, 20.0)
    assert result.npv_egp is None
    assert WARNING_NPV_DELIVERY_MONTH_UNKNOWN in result.warnings


def test_bank_plan_without_delivery_is_known():
    # For bank plans delivery None means "none", the contract adds no warning
    plan = bank_plan(1_000_000.0, 10.0, 20.0, 5)
    assert plan.delivery_payment_egp is None
    assert plan_npv(plan, 20.0).npv_egp is not None


def test_plan_npv_does_not_change_input_and_keeps_warnings():
    plan = example_plan()
    result = plan_npv(plan, 20.0)
    assert plan.npv_egp is None and plan.annual_discount_rate_pct is None
    assert result.annual_discount_rate_pct == 20.0
    again = plan_npv(dev_plan(delivery_payment_egp=None), 20.0)
    assert again.warnings.count(WARNING_NPV_DELIVERY_UNKNOWN) == 1


# ---- bad inputs fail loudly ----

@pytest.mark.parametrize("rate", [-1.0, -0.0001, math.nan, math.inf])
def test_bad_rate_raises(rate):
    with pytest.raises(ValueError):
        npv([(0, 1.0)], rate)
    with pytest.raises(ValueError):
        plan_npv(example_plan(), rate)


@pytest.mark.parametrize("rate", [True, "20", None])
def test_non_number_rate_raises(rate):
    # None must never be read as 0 %
    with pytest.raises(TypeError):
        npv([(0, 1.0)], rate)
    with pytest.raises(TypeError):
        plan_npv(example_plan(), rate)


def test_empty_cashflows_raise_instead_of_zero():
    with pytest.raises(ValueError):
        npv([], 10.0)


@pytest.mark.parametrize("flow", [(-1, 1.0), (1.5, 1.0), (True, 1.0), (1, -5.0), (1, math.nan)])
def test_bad_cashflow_raises(flow):
    with pytest.raises(ValueError):
        npv([flow], 10.0)


def test_total_paid_mismatch_raises():
    # PlanResult rejects this when validated; model_copy skips validation, so npv() checks too.
    broken = dev_plan().model_copy(update={"total_paid_egp": 999_000.0})
    with pytest.raises(ValueError, match="total_paid_egp"):
        plan_cashflows(broken)


# ---- cash flows come from PlanResult.payments, not from inferred frequency ----

def test_months_are_read_from_the_table_not_inferred():
    # Installments in months 12 and 24 are neither monthly nor quarterly; the old code
    # could not read them. 25 %: 100,000 + 100,000 / 1.25 + 100,000 / 1.25^2 = 244,000
    plan = dev_plan(
        step=12, price_egp=300_000.0, down_payment_egp=100_000.0, down_payment_pct=100 / 3,
        installment_count=2, installment_egp=100_000.0, monthly_equivalent_egp=100_000.0 / 12,
        total_paid_egp=300_000.0,
    )
    assert plan_cashflows(plan) == [(0, 100_000.0), (12, 100_000.0), (24, 100_000.0)]
    assert plan_npv(plan, 25.0).npv_egp == pytest.approx(244_000.0, abs=1e-6)


def test_monthly_equivalent_does_not_change_the_npv():
    # Same table, different monthly_equivalent_egp: npv() ignores it now.
    a = dev_plan()
    b = dev_plan(monthly_equivalent_egp=200_000.0)
    assert plan_npv(a, 20.0).npv_egp == plan_npv(b, 20.0).npv_egp


def test_maintenance_rows_are_left_out():
    data = example_plan().model_dump()
    data["payments"].append({"month": 96, "amount_egp": 50_000.0, "type": "maintenance"})
    plan = PlanResult.model_validate(data)
    flows = plan_cashflows(plan)
    assert len(flows) == len(data["payments"]) - 1
    assert npv(flows, 0.0) == plan.total_paid_egp


def test_plan_without_payment_table_gives_none_not_rebuilt():
    # Behaviour change: before, npv() rebuilt the schedule from installment fields.
    # Now a PlanResult with payments=None has an unknown NPV.
    plan = bank_plan(1_000_000.0, 10.0, 20.0, 5).model_copy(update={"payments": None})
    assert plan_cashflows(plan) is None
    result = plan_npv(plan, 20.0)
    assert result.npv_egp is None
    assert result.annual_discount_rate_pct is None
    assert WARNING_NPV_PAYMENTS_UNKNOWN in result.warnings


def test_zero_down_row_is_kept_in_month_zero():
    plan = dev_plan(down_payment_egp=0.0, down_payment_pct=0.0, installment_egp=250_000.0,
                    monthly_equivalent_egp=250_000.0 / 3)
    assert plan_cashflows(plan)[0] == (0, 0.0)
