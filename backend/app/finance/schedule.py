"""S1-T3-1 / S1-T3-2 / S2-M5-01: payment tables for developer plans and bank loans.

Pure code: no LLM call, no network, no I/O, no randomness. Every number comes from the inputs.
Rules come from docs/calculator-reference/README.md and the PlanResult validators in
app/contracts.py:

* Developer plan: down payment in month 0, equal installments (monthly 1..n or quarterly
  3, 6, 9...), the delivery payment in ``delivery_month``. No rounding is applied, so every
  installment row equals ``installment_egp`` exactly.
* Bank loan: loan = price - down, monthly PMT for ``years * 12`` months,
  ``total_paid = down + PMT * n``. Matches Google Sheets ``=PMT(rate/12, n, -loan)``.
* Unknown stays unknown: an unpublished delivery payment or delivery month gives
  ``payments=None`` and a warning (added by PlanResult itself). It is never treated as 0.
* Maintenance is informative only. It is not part of the price, total paid or NPV, and the
  sources do not say in which month it is paid, so no maintenance row is invented.

The PMT formula and the bank-loan amortization table follow the approach Mohamed Elekhnawy
wrote in ``feat/S1-T3-2-mortgage-schedule``, moved onto the shared contracts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

from app.contracts import Listing, Payment, PaymentPlan, PlanResult
from app.finance.calculator import plan_npv

_ABS_TOL_EGP = 0.01


class PlanNotComputable(ValueError):
    """The published inputs are not enough to build a PlanResult (e.g. no down payment at all).

    ``missing_fields`` names what is missing so the caller can show "not published".
    """

    def __init__(self, message: str, missing_fields: list[str]):
        super().__init__(message)
        self.missing_fields = missing_fields


def _installments_per_year(frequency: str) -> int:
    if frequency == "monthly":
        return 12
    if frequency == "quarterly":
        return 4
    raise ValueError(f"unsupported frequency: {frequency!r}")


def _down_payment(plan: PaymentPlan, price_egp: float) -> tuple[float, float]:
    """(down_egp, down_pct) from whichever value the source published."""
    if plan.down_payment_source == "egp" and plan.down_payment_egp is not None:
        down = float(plan.down_payment_egp)
        return down, down / price_egp * 100.0
    if plan.down_payment_source == "pct" and plan.down_payment_pct is not None:
        pct = float(plan.down_payment_pct)
        return price_egp * pct / 100.0, pct
    raise PlanNotComputable(
        f"plan {plan.plan_id}: the down payment was not published",
        ["down_payment_egp", "down_payment_pct"],
    )


def developer_schedule(plan: PaymentPlan, *, listing_id: str, price_egp: float) -> PlanResult:
    """Payment table of one developer plan for one listing.

    Raises ``PlanNotComputable`` when the down payment is unknown, and ``ValueError`` when the
    published numbers contradict each other (down + delivery above the price, or money left
    to pay with zero installments).
    """
    if not (isinstance(price_egp, (int, float)) and math.isfinite(price_egp) and price_egp > 0):
        raise ValueError(f"price_egp must be a finite number > 0, got {price_egp!r}")

    down, down_pct = _down_payment(plan, price_egp)
    count = plan.years * _installments_per_year(plan.frequency)

    delivery: float | None = None
    if plan.delivery_payment_pct is not None:
        delivery = price_egp * float(plan.delivery_payment_pct) / 100.0

    installment: float | None = None
    monthly_equivalent: float | None = None
    if delivery is not None:
        remaining = price_egp - down - delivery
        if remaining < -_ABS_TOL_EGP:
            raise ValueError(f"plan {plan.plan_id}: down + delivery payment is more than the price")
        remaining = max(0.0, remaining)
        if count == 0:
            if remaining > _ABS_TOL_EGP:
                raise ValueError(f"plan {plan.plan_id}: money left to pay but zero installments")
            installment = 0.0
        elif remaining <= _ABS_TOL_EGP:
            # 100% paid up front (down + delivery): nothing to spread over installments.
            count = 0
            installment = 0.0
        else:
            installment = remaining / count
        monthly_equivalent = installment / (3.0 if plan.frequency == "quarterly" else 1.0)

    payments: list[Payment] | None = None
    needs_month = delivery is not None and delivery > 0
    if installment is not None and (not needs_month or plan.delivery_month is not None):
        step = 1 if plan.frequency == "monthly" else 3
        rows = [Payment(month=0, amount_egp=down, type="down_payment")]
        rows += [
            Payment(month=i * step, amount_egp=installment, type="installment")
            for i in range(1, count + 1)
        ]
        if needs_month:
            rows.append(Payment(month=plan.delivery_month, amount_egp=delivery, type="delivery"))
        rows.sort(key=lambda p: p.month)  # stable: delivery stays after an installment in its month
        payments = rows

    return PlanResult(
        listing_id=listing_id,
        plan_id=plan.plan_id,
        plan_type="developer",
        price_egp=price_egp,
        down_payment_egp=down,
        down_payment_pct=down_pct,
        delivery_payment_egp=delivery,
        delivery_month=plan.delivery_month if needs_month else None,
        installment_count=count,
        installment_egp=installment,
        monthly_equivalent_egp=monthly_equivalent,
        # 0% interest: whatever the split, the buyer pays exactly the price (maintenance excluded).
        total_paid_egp=price_egp,
        payments=payments,
    )


def pmt(loan_egp: float, annual_rate_pct: float, months: int) -> float:
    """Fixed monthly payment of a loan, same as Google Sheets ``=PMT(rate/12, months, -loan)``."""
    if months <= 0:
        raise ValueError("months must be > 0")
    if annual_rate_pct < 0 or not math.isfinite(annual_rate_pct):
        raise ValueError("annual_rate_pct must be a finite number >= 0")
    r = annual_rate_pct / 100.0 / 12.0
    if r == 0:
        return loan_egp / months
    return loan_egp * r / (1.0 - (1.0 + r) ** (-months))


def mortgage_schedule(
    *,
    listing_id: str,
    plan_id: str,
    price_egp: float,
    down_payment_egp: float,
    annual_interest_rate_pct: float,
    years: int,
) -> PlanResult:
    """Payment table of a bank loan: down payment in month 0, then ``years * 12`` equal PMTs."""
    if not (math.isfinite(price_egp) and price_egp > 0):
        raise ValueError("price_egp must be a finite number > 0")
    if not (0 <= down_payment_egp <= price_egp + _ABS_TOL_EGP):
        raise ValueError("down_payment_egp must be between 0 and the price")
    if years < 0:
        raise ValueError("years must be >= 0")

    loan = max(0.0, price_egp - down_payment_egp)
    months = years * 12
    if loan <= _ABS_TOL_EGP or months == 0:
        if loan > _ABS_TOL_EGP:
            raise ValueError("a loan needs years > 0")
        months, payment = 0, 0.0
    else:
        payment = pmt(loan, annual_interest_rate_pct, months)

    rows = [Payment(month=0, amount_egp=down_payment_egp, type="down_payment")]
    rows += [Payment(month=m, amount_egp=payment, type="installment") for m in range(1, months + 1)]

    return PlanResult(
        listing_id=listing_id,
        plan_id=plan_id,
        plan_type="bank",
        price_egp=price_egp,
        down_payment_egp=down_payment_egp,
        down_payment_pct=down_payment_egp / price_egp * 100.0,
        delivery_payment_egp=0.0,  # a bank loan has no delivery payment (a real zero)
        delivery_month=None,
        installment_count=months,
        installment_egp=payment,
        monthly_equivalent_egp=payment,
        total_paid_egp=down_payment_egp + payment * months,
        payments=rows,
    )


@dataclass(frozen=True)
class AmortizationRow:
    month: int
    payment_egp: float
    interest_egp: float
    principal_egp: float
    balance_egp: float


def mortgage_amortization(loan_egp: float, annual_interest_rate_pct: float, years: int) -> list[AmortizationRow]:
    """Month-by-month split of each PMT into interest and principal. The final balance is 0."""
    months = years * 12
    payment = pmt(loan_egp, annual_interest_rate_pct, months)
    r = annual_interest_rate_pct / 100.0 / 12.0
    balance = loan_egp
    rows: list[AmortizationRow] = []
    for m in range(1, months + 1):
        interest = balance * r
        principal = payment - interest
        balance = balance - principal
        if m == months:
            balance = 0.0 if abs(balance) < _ABS_TOL_EGP else balance
        rows.append(AmortizationRow(m, payment, interest, principal, balance))
    return rows


def months_between(start: date, end: date) -> int:
    """Whole calendar months from ``start`` to ``end``; 0 if ``end`` is not after ``start``."""
    return max(0, (end.year - start.year) * 12 + (end.month - start.month))


def plan_from_listing(listing: Listing, *, as_of: date | None = None) -> PaymentPlan:
    """The headline developer plan published on a listing, as a PaymentPlan.

    ``delivery_month`` is counted from ``as_of`` (the contract date) to ``listing.delivery_date``.
    Without ``as_of`` or without a delivery date it stays unknown (None); nothing is guessed.
    """
    if listing.years is None or listing.frequency is None or listing.down_payment_pct is None:
        raise ValueError(
            f"listing {listing.listing_id} has no full payment plan "
            "(years, frequency or down_payment_pct unknown)"
        )
    delivery_month = None
    if as_of is not None and listing.delivery_date is not None:
        delivery_month = months_between(as_of, listing.delivery_date)
    return PaymentPlan(
        plan_id=f"P-{listing.listing_id}",
        down_payment_egp=None,
        down_payment_pct=listing.down_payment_pct,
        down_payment_source="pct",
        years=listing.years,
        frequency=listing.frequency,
        delivery_payment_pct=listing.delivery_payment_pct,
        delivery_month=delivery_month,
        maintenance_pct=listing.maintenance_pct,
    )


def build_plan(
    listing: Listing,
    plan: PaymentPlan | None = None,
    *,
    as_of: date | None = None,
    annual_discount_rate_pct: float | None = None,
) -> PlanResult:
    """Listing (+ optional stored plan) -> PlanResult, with NPV when a discount rate is given.

    This is ``Finance.build_plan`` from the Sprint 2 contract pack. The discount rate always
    comes from the caller; there is no default.
    """
    if listing.listing_id is None:
        raise ValueError("listing has no listing_id yet (not ingested)")
    plan = plan or plan_from_listing(listing, as_of=as_of)
    result = developer_schedule(plan, listing_id=listing.listing_id, price_egp=listing.price_egp)
    if annual_discount_rate_pct is not None:
        result = plan_npv(result, annual_discount_rate_pct)
    return result
