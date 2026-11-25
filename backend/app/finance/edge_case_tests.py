"""
Additional edge case tests for developer_schedule().
"""
import sys
from pathlib import Path
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.finance import (
    developer_schedule,
    PaymentPlan,
    PaymentFrequency,
)


def test_invalid_inputs():
    """Test validation of invalid inputs."""
    print("\n=== Test: Invalid inputs ===")
    
    # Test negative price
    try:
        plan = PaymentPlan(
            price=Decimal("-1000"),
            down_payment_pct=Decimal("20"),
            years=5,
            frequency=PaymentFrequency.MONTHLY,
        )
        developer_schedule(plan)
        assert False, "Should have raised ValueError for negative price"
    except ValueError as e:
        print(f"[PASSED] Negative price rejected: {e}")
    
    # Test down payment > 100%
    try:
        plan = PaymentPlan(
            price=Decimal("1000000"),
            down_payment_pct=Decimal("150"),
            years=5,
            frequency=PaymentFrequency.MONTHLY,
        )
        developer_schedule(plan)
        assert False, "Should have raised ValueError for down payment > 100%"
    except ValueError as e:
        print(f"[PASSED] Down payment > 100% rejected: {e}")
    
    # Test down payment + delivery > 100%
    try:
        plan = PaymentPlan(
            price=Decimal("1000000"),
            down_payment_pct=Decimal("70"),
            years=5,
            frequency=PaymentFrequency.MONTHLY,
            delivery_pct=Decimal("50"),
            delivery_month=36,
        )
        developer_schedule(plan)
        assert False, "Should have raised ValueError for down + delivery > 100%"
    except ValueError as e:
        print(f"[PASSED] Down + delivery > 100% rejected: {e}")
    
    # Test delivery without month
    try:
        plan = PaymentPlan(
            price=Decimal("1000000"),
            down_payment_pct=Decimal("20"),
            years=5,
            frequency=PaymentFrequency.MONTHLY,
            delivery_pct=Decimal("10"),
            delivery_month=None,
        )
        developer_schedule(plan)
        assert False, "Should have raised ValueError for delivery without month"
    except ValueError as e:
        print(f"[PASSED] Delivery without month rejected: {e}")
    
    # Test negative maintenance
    try:
        plan = PaymentPlan(
            price=Decimal("1000000"),
            down_payment_pct=Decimal("20"),
            years=5,
            frequency=PaymentFrequency.MONTHLY,
            maintenance=Decimal("-100"),
        )
        developer_schedule(plan)
        assert False, "Should have raised ValueError for negative maintenance"
    except ValueError as e:
        print(f"[PASSED] Negative maintenance rejected: {e}")


def test_zero_values():
    """Test explicit zero values vs None."""
    print("\n=== Test: Zero vs None ===")
    
    # Test explicit 0% down payment
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=Decimal("0"),
        years=5,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    assert result.down_payment == Decimal("0"), "0% down should produce Decimal('0')"
    assert result.down_payment is not None, "0% down should not be None"
    print(f"[PASSED] 0% down payment: {result.down_payment} (not None)")
    
    # Test None down payment
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=None,
        years=5,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    assert result.down_payment is None, "None down_payment_pct should remain None"
    print(f"[PASSED] None down payment: {result.down_payment}")
    
    # Test explicit 0% delivery
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=Decimal("20"),
        years=5,
        frequency=PaymentFrequency.MONTHLY,
        delivery_pct=Decimal("0"),
        delivery_month=36,
    )
    result = developer_schedule(plan)
    
    assert result.delivery_payment == Decimal("0"), "0% delivery should produce Decimal('0')"
    print(f"[PASSED] 0% delivery: {result.delivery_payment}")


def test_small_amounts():
    """Test rounding with very small amounts."""
    print("\n=== Test: Small amounts ===")
    
    plan = PaymentPlan(
        price=Decimal("1000.33"),
        down_payment_pct=Decimal("10.5"),
        years=1,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    # Verify reconciliation even with small amounts
    from backend.app.finance import PaymentType
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total_installments = sum(p.amount for p in installments)
    
    expected_down = Decimal("105.03")  # 1000.33 * 0.105 = 105.03465, rounded to 105.03
    expected_remaining = Decimal("895.30")  # 1000.33 - 105.03
    
    assert result.down_payment == expected_down
    assert total_installments == expected_remaining
    assert result.down_payment + total_installments == plan.price
    
    print(f"[PASSED] Small price: {plan.price}")
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Installments total: {total_installments}")
    print(f"[PASSED] Reconciliation: {result.down_payment + total_installments} = {plan.price}")


def test_large_amounts():
    """Test with large property prices."""
    print("\n=== Test: Large amounts ===")
    
    plan = PaymentPlan(
        price=Decimal("50000000.99"),
        down_payment_pct=Decimal("25"),
        years=10,
        frequency=PaymentFrequency.QUARTERLY,
    )
    result = developer_schedule(plan)
    
    # Verify reconciliation with large amounts
    from backend.app.finance import PaymentType
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total_installments = sum(p.amount for p in installments)
    
    assert result.down_payment + total_installments == plan.price
    
    print(f"[PASSED] Large price: {plan.price}")
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Installments: {result.total_installments}")
    print(f"[PASSED] Regular installment: {result.installment_amount}")
    print(f"[PASSED] Last installment: {installments[-1].amount}")
    print(f"[PASSED] Reconciliation verified")


def test_one_year_monthly():
    """Test minimum viable plan: 1 year monthly."""
    print("\n=== Test: One year monthly ===")
    
    plan = PaymentPlan(
        price=Decimal("100000"),
        down_payment_pct=Decimal("30"),
        years=1,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    assert result.total_installments == 12
    
    from backend.app.finance import PaymentType
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    assert len(installments) == 12
    assert installments[0].month == 1
    assert installments[-1].month == 12
    
    print(f"[PASSED] 1 year = 12 monthly installments")
    print(f"[PASSED] Months: {installments[0].month} to {installments[-1].month}")


def test_one_year_quarterly():
    """Test minimum viable plan: 1 year quarterly."""
    print("\n=== Test: One year quarterly ===")
    
    plan = PaymentPlan(
        price=Decimal("100000"),
        down_payment_pct=Decimal("30"),
        years=1,
        frequency=PaymentFrequency.QUARTERLY,
    )
    result = developer_schedule(plan)
    
    assert result.total_installments == 4
    
    from backend.app.finance import PaymentType
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    assert len(installments) == 4
    
    expected_months = [3, 6, 9, 12]
    actual_months = [p.month for p in installments]
    assert actual_months == expected_months
    
    print(f"[PASSED] 1 year = 4 quarterly installments")
    print(f"[PASSED] Months: {actual_months}")


def run_all_tests():
    """Run all edge case tests."""
    print("=" * 60)
    print("EDGE CASE TESTS")
    print("=" * 60)
    
    try:
        test_invalid_inputs()
        test_zero_values()
        test_small_amounts()
        test_large_amounts()
        test_one_year_monthly()
        test_one_year_quarterly()
        
        print("\n" + "=" * 60)
        print("ALL EDGE CASE TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
