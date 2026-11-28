"""S1-T6-1 / S2-M5-02: can THIS customer pay THIS plan?

Deterministic, no LLM. Compares the plan's down payment with the down payment the customer
has, and the plan's monthly-equivalent installment with what the customer can pay a month.
It also checks whether a delivery payment is left uncovered. It never asks for income.

Statuses (thresholds in affordability_config.json, never hard-coded in the agent):
* ``fit``      both amounts within the customer's limits and no uncovered delivery payment
* ``tight``    over a limit by up to ``tight_limit_pct``, or the delivery payment is not covered
* ``not_fit``  over a limit by more than ``tight_limit_pct``
* ``unknown``  a customer input or a plan amount is unknown (``missing_fields`` says which)

The ``reason`` text is a fixed Egyptian-Arabic template with no digits (the contract rejects
digits). Every number travels in the numeric fields.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from app.contracts import AffordabilityResult, PlanResult, Slots

_CONFIG = Path(__file__).with_name("affordability_config.json")

REASON_FIT = "المقدم والقسط في حدود اللي حضرتك قلته."
REASON_TIGHT_OVER = "قريبة من حدودك، بس المقدم أو القسط أعلى شوية من اللي قلته."
REASON_TIGHT_DELIVERY = "المقدم والقسط مناسبين، بس دفعة الاستلام مش متغطية من المقدم المتاح."
REASON_NOT_FIT = "المقدم أو القسط أعلى بكتير من الحدود اللي حضرتك قلتها."
REASON_NOT_FIT_DELIVERY = "المقدم أو القسط أعلى بكتير من حدودك، وكمان دفعة الاستلام مش متغطية."
REASON_UNKNOWN_CUSTOMER = "محتاجين نعرف المقدم والقسط المناسبين ليك عشان نحكم."
REASON_UNKNOWN_PLAN = "خطة السداد ناقصة بيانات منشورة، فمش هنقدر نحكم دلوقتي."

FLAG_DELIVERY = "delivery_payment"
FLAG_DOWN_SHORT = "down_payment_short"
FLAG_MONTHLY_SHORT = "monthly_short"


@lru_cache(maxsize=1)
def load_config() -> dict:
    with _CONFIG.open(encoding="utf-8") as f:
        cfg = json.load(f)
    limit = cfg.get("tight_limit_pct")
    if not isinstance(limit, (int, float)) or isinstance(limit, bool) or limit < 0:
        raise ValueError("affordability_config.json: tight_limit_pct must be a number >= 0")
    return cfg


def _over_ratio(required: float, available: float) -> float:
    """How far ``required`` is above ``available`` (0.1 = 10 % over). <= 0 means covered."""
    if available > 0:
        return required / available - 1.0
    return math.inf if required > 0 else 0.0


def check_affordability(
    plan: PlanResult,
    down_payment_available_egp: float | None,
    monthly_capacity_egp: float | None,
    *,
    tight_limit_pct: float | None = None,
) -> AffordabilityResult:
    """Affordability of one plan for one customer. ``tight_limit_pct`` overrides the config (tests)."""
    limit = (load_config()["tight_limit_pct"] if tight_limit_pct is None else tight_limit_pct) / 100.0
    down_req = plan.down_payment_egp
    mon_req = plan.monthly_equivalent_egp

    def gap(req: float | None, avail: float | None) -> float | None:
        return None if req is None or avail is None else req - avail

    base = {
        "listing_id": plan.listing_id,
        "plan_id": plan.plan_id,
        "down_payment_required_egp": down_req,
        "down_payment_available_egp": down_payment_available_egp,
        "down_payment_gap_egp": gap(down_req, down_payment_available_egp),
        "monthly_required_egp": mon_req,
        "monthly_capacity_egp": monthly_capacity_egp,
        "monthly_gap_egp": gap(mon_req, monthly_capacity_egp),
    }

    customer_missing = [
        name
        for name, value in (
            ("down_payment_available_egp", down_payment_available_egp),
            ("monthly_capacity_egp", monthly_capacity_egp),
        )
        if value is None
    ]
    plan_missing = [] if mon_req is not None else ["monthly_required_egp"]
    if customer_missing or plan_missing:
        return AffordabilityResult(
            **base,
            status="unknown",
            reason=REASON_UNKNOWN_CUSTOMER if customer_missing else REASON_UNKNOWN_PLAN,
            flags=[],
            missing_fields=customer_missing + plan_missing,
        )

    down_over = _over_ratio(down_req, down_payment_available_egp)
    mon_over = _over_ratio(mon_req, monthly_capacity_egp)
    over = max(down_over, mon_over)

    delivery = plan.delivery_payment_egp or 0.0
    left_after_down = down_payment_available_egp - down_req
    delivery_uncovered = delivery > 0 and left_after_down < delivery - 1e-9

    flags: list[str] = []
    if down_over > 1e-12:
        flags.append(FLAG_DOWN_SHORT)
    if mon_over > 1e-12:
        flags.append(FLAG_MONTHLY_SHORT)
    if delivery_uncovered:
        flags.append(FLAG_DELIVERY)

    if over > limit + 1e-12:
        status, reason = "not_fit", (REASON_NOT_FIT_DELIVERY if delivery_uncovered else REASON_NOT_FIT)
    elif over > 1e-12:
        status, reason = "tight", REASON_TIGHT_OVER
    elif delivery_uncovered and load_config().get("uncovered_delivery_is_tight", True):
        status, reason = "tight", REASON_TIGHT_DELIVERY
    else:
        status, reason = "fit", REASON_FIT

    return AffordabilityResult(**base, status=status, reason=reason, flags=flags, missing_fields=[])


def check_affordability_for_slots(plan: PlanResult, slots: Slots) -> AffordabilityResult:
    """Same check using the customer's slots. Only CONFIRMED values are used (score rule)."""
    down = slots.down_payment_available_egp
    monthly = slots.monthly_capacity_egp
    return check_affordability(
        plan,
        down.value if down.confirmed else None,
        monthly.value if monthly.confirmed else None,
    )
