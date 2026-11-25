"""S1-T3-3: net present value (NPV) of a payment plan.

Pure code: no LLM call, no network call, no I/O. Every number here comes from the
inputs; nothing is invented or defaulted.

Rate convention (Convention A, agreed in docs/calculator-reference/README.md)
-----------------------------------------------------------------------------
* ``monthly_rate = (1 + annual_rate) ** (1 / 12) - 1``   (effective monthly compounding)
* A payment in month ``t`` is worth ``amount / (1 + monthly_rate) ** t`` today.
* Month 0 (the down payment) is not discounted: its factor is exactly 1.
* At an annual rate of 0 % every factor is 1, so NPV == the plain total of payments.
* Maintenance fees are not part of the price and are never included.

The discount rate is always passed in by the caller. There is no default here on
purpose: which rate AqarAI uses (CBE rate, inflation, a fixed product choice) is an
open team decision and must not be hidden inside the calculator.

Cash flows come from ``PlanResult.payments`` (the payment table the calculator built).
npv() never rebuilds the schedule itself and never guesses the installment frequency.

Unknown stays unknown: if the payment table is ``None`` (for example a developer plan
whose delivery payment was not published), the NPV is ``None`` with a warning. It is
never computed as if a missing payment were 0.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from app.contracts import PlanResult

Cashflow = tuple[int, float]  # (month after contract, amount in EGP)

# Float noise allowance when comparing sums computed by code. Not a data tolerance.
_REL_TOL = 1e-9
_ABS_TOL_EGP = 0.01

WARNING_NPV_DELIVERY_UNKNOWN = "npv_unknown_delivery_payment"
WARNING_NPV_DELIVERY_MONTH_UNKNOWN = "npv_unknown_delivery_month"
WARNING_NPV_PAYMENTS_UNKNOWN = "npv_unknown_payment_table"


def monthly_rate(annual_discount_rate_pct: float) -> float:
    """Convert a yearly discount rate in percent (e.g. ``20.0``) to the effective monthly rate.

    Raises ``ValueError`` for a negative, NaN or infinite rate, ``TypeError`` for a non-number.
    """
    _check_rate(annual_discount_rate_pct)
    return (1.0 + annual_discount_rate_pct / 100.0) ** (1.0 / 12.0) - 1.0


def npv(cashflows: Sequence[Cashflow], annual_discount_rate_pct: float) -> float:
    """Present value in EGP of ``(month, amount)`` payments at a yearly discount rate in percent.

    ``NPV = sum(amount_t / (1 + monthly_rate) ** t)`` with Convention A (see module docstring).
    Several payments in the same month are allowed and simply add up.

    Raises ``ValueError`` when:
    * ``cashflows`` is empty (no payments is "unknown", not an NPV of 0),
    * a month is not a whole number >= 0,
    * an amount is negative, NaN or infinite,
    * the rate is negative, NaN or infinite (``TypeError`` if it is not a number).
    """
    m = monthly_rate(annual_discount_rate_pct)
    if len(cashflows) == 0:
        raise ValueError("cashflows is empty: cannot compute an NPV with no payments")

    total = 0.0
    for month, amount in cashflows:
        if isinstance(month, bool) or not isinstance(month, int) or month < 0:
            raise ValueError(f"month must be an int >= 0, got {month!r}")
        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"amount must be a finite number >= 0, got {amount!r}")
        total += amount / (1.0 + m) ** month
    return total


def plan_cashflows(plan: PlanResult) -> list[Cashflow] | None:
    """Read the ``(month, amount)`` cash flows from ``plan.payments``.

    Every row is used as it is (down payment, installments, delivery), in table order.
    Maintenance rows are left out: they are not part of the price (README, Convention A).

    Returns ``None`` when ``plan.payments`` is ``None``, which means the payment table is
    unknown (for example the delivery payment or its month was not published).

    Raises ``ValueError`` if the rows do not add up to ``total_paid_egp``. PlanResult already
    checks this when it is built; the check here catches objects that skipped validation.
    """
    if plan.payments is None:
        return None

    flows: list[Cashflow] = [
        (p.month, p.amount_egp) for p in plan.payments if p.type != "maintenance"
    ]
    paid = sum(amount for _, amount in flows)
    if not math.isclose(paid, plan.total_paid_egp, rel_tol=_REL_TOL, abs_tol=_ABS_TOL_EGP):
        raise ValueError(
            f"payments add up to {paid!r} but total_paid_egp is {plan.total_paid_egp!r}"
        )
    return flows


def plan_npv(plan: PlanResult, annual_discount_rate_pct: float) -> PlanResult:
    """Return a copy of ``plan`` with ``npv_egp`` and ``annual_discount_rate_pct`` filled in.

    If the cash flows are unknown (see ``plan_cashflows``), both stay ``None`` and a warning
    explains why. The input object is not changed.
    """
    _check_rate(annual_discount_rate_pct)
    data = plan.model_dump()
    warnings = list(plan.warnings)

    flows = plan_cashflows(plan)
    if flows is None:
        reason = _unknown_reason(plan)
        if reason not in warnings:
            warnings.append(reason)
        data.update(npv_egp=None, annual_discount_rate_pct=None, warnings=warnings)
    else:
        data.update(
            npv_egp=npv(flows, annual_discount_rate_pct),
            annual_discount_rate_pct=annual_discount_rate_pct,
            warnings=warnings,
        )
    return PlanResult.model_validate(data)


def _unknown_reason(plan: PlanResult) -> str:
    """Why the payment table is unknown, as a warning code."""
    delivery = plan.delivery_payment_egp
    if plan.plan_type == "developer" and delivery is None:
        return WARNING_NPV_DELIVERY_UNKNOWN
    if delivery is not None and delivery > 0 and plan.delivery_month is None:
        return WARNING_NPV_DELIVERY_MONTH_UNKNOWN
    return WARNING_NPV_PAYMENTS_UNKNOWN


def _check_rate(annual_discount_rate_pct: float) -> None:
    if isinstance(annual_discount_rate_pct, bool) or not isinstance(
        annual_discount_rate_pct, (int, float)
    ):
        raise TypeError(
            f"annual_discount_rate_pct must be a number, got {annual_discount_rate_pct!r}"
        )
    if not math.isfinite(annual_discount_rate_pct) or annual_discount_rate_pct < 0:
        raise ValueError(
            f"annual_discount_rate_pct must be a finite number >= 0, got {annual_discount_rate_pct!r}"
        )
