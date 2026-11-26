"""S2: tests for roi_estimate(). Expected values worked out by hand."""

import math
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.finance.roi import roi_estimate


def test_full_example():
    # price 2,000,000, rent 120,000 a year, +10% a year, 2 years, costs 20,000 a year
    # yield 6%; value 2,000,000 x 1.1^2 = 2,420,000; rent 240,000; costs 40,000
    # return = 420,000 + 240,000 - 40,000 = 620,000 = 31%; yearly = sqrt(1.31) - 1
    r = roi_estimate(2_000_000, years=2, expected_annual_rent_egp=120_000, annual_appreciation_pct=10, annual_costs_egp=20_000)
    assert r.gross_yield_pct == pytest.approx(6.0)
    assert r.future_value_egp == pytest.approx(2_420_000)
    assert r.total_return_egp == pytest.approx(620_000)
    assert r.total_return_pct == pytest.approx(31.0)
    assert r.annualized_return_pct == pytest.approx((math.sqrt(1.31) - 1) * 100)
    assert r.missing_fields == []


def test_missing_inputs_stay_unknown():
    r = roi_estimate(2_000_000, years=5, expected_annual_rent_egp=100_000, annual_appreciation_pct=None)
    assert r.gross_yield_pct == pytest.approx(5.0)
    assert r.future_value_egp is None
    assert r.total_return_egp is None
    assert set(r.missing_fields) == {"annual_appreciation_pct", "annual_costs_egp"}


def test_zero_costs_only_when_given():
    r = roi_estimate(1_000_000, years=1, expected_annual_rent_egp=0, annual_appreciation_pct=0, annual_costs_egp=0)
    assert r.total_return_egp == 0


@pytest.mark.parametrize("bad", [{"years": 0}, {"years": 1, "expected_annual_rent_egp": -1}])
def test_rejects_bad_input(bad):
    kw = {"years": 1, "expected_annual_rent_egp": 1, "annual_appreciation_pct": 1}
    kw.update(bad)
    with pytest.raises(ValueError):
        roi_estimate(1_000_000, **kw)
