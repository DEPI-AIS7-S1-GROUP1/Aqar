"""S2-M5-02: simple return-on-investment estimate for customers who buy to invest.

Every input is explicit and comes from the caller (the customer or sourced data); nothing is
defaulted. A missing input makes the outputs that need it ``None`` (unknown), never 0.

Formulas (documented so the committee can check them by hand):
* gross_yield_pct      = expected_annual_rent / price * 100
* future_value_egp     = price * (1 + annual_appreciation_pct / 100) ** years
* total_rent_egp       = expected_annual_rent * years            (no rent growth assumed)
* total_costs_egp      = annual_costs * years                     (0 only if the caller says 0)
* total_return_egp     = (future_value - price) + total_rent - total_costs
* total_return_pct     = total_return / price * 100
* annualized_return_pct= ((price + total_return) / price) ** (1 / years) - 1, in percent
It ignores financing costs and taxes; the write-up should say so.
"""

from __future__ import annotations

import math

from pydantic import BaseModel, Field


class RoiResult(BaseModel):
    price_egp: float = Field(gt=0)
    years: int = Field(gt=0)
    gross_yield_pct: float | None = None
    future_value_egp: float | None = None
    total_rent_egp: float | None = None
    total_costs_egp: float | None = None
    total_return_egp: float | None = None
    total_return_pct: float | None = None
    annualized_return_pct: float | None = None
    missing_fields: list[str] = []


def _ok(x: float | None) -> bool:
    return x is not None and not isinstance(x, bool) and math.isfinite(x)


def roi_estimate(
    price_egp: float,
    *,
    years: int,
    expected_annual_rent_egp: float | None,
    annual_appreciation_pct: float | None,
    annual_costs_egp: float | None = None,
) -> RoiResult:
    if not (_ok(price_egp) and price_egp > 0):
        raise ValueError("price_egp must be a finite number > 0")
    if isinstance(years, bool) or not isinstance(years, int) or years <= 0:
        raise ValueError("years must be an int > 0")
    for name, v in (
        ("expected_annual_rent_egp", expected_annual_rent_egp),
        ("annual_costs_egp", annual_costs_egp),
    ):
        if v is not None and not (_ok(v) and v >= 0):
            raise ValueError(f"{name} must be a finite number >= 0")
    if annual_appreciation_pct is not None and not (_ok(annual_appreciation_pct) and annual_appreciation_pct > -100):
        raise ValueError("annual_appreciation_pct must be a finite number > -100")

    missing: list[str] = []
    rent = expected_annual_rent_egp
    if rent is None:
        missing.append("expected_annual_rent_egp")
    if annual_appreciation_pct is None:
        missing.append("annual_appreciation_pct")
    if annual_costs_egp is None:
        missing.append("annual_costs_egp")

    gross_yield = None if rent is None else rent / price_egp * 100.0
    future_value = (
        None if annual_appreciation_pct is None else price_egp * (1.0 + annual_appreciation_pct / 100.0) ** years
    )
    total_rent = None if rent is None else rent * years
    total_costs = None if annual_costs_egp is None else annual_costs_egp * years

    total_return = None
    total_return_pct = None
    annualized = None
    if future_value is not None and total_rent is not None and total_costs is not None:
        total_return = (future_value - price_egp) + total_rent - total_costs
        total_return_pct = total_return / price_egp * 100.0
        end_value = price_egp + total_return
        if end_value > 0:
            annualized = ((end_value / price_egp) ** (1.0 / years) - 1.0) * 100.0

    return RoiResult(
        price_egp=price_egp,
        years=years,
        gross_yield_pct=gross_yield,
        future_value_egp=future_value,
        total_rent_egp=total_rent,
        total_costs_egp=total_costs,
        total_return_egp=total_return,
        total_return_pct=total_return_pct,
        annualized_return_pct=annualized,
        missing_fields=missing,
    )
