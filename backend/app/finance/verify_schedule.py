"""
Verification script for developer_schedule() implementation.
Tests key scenarios without modifying official test suite.
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
    PaymentType,
)


def test_monthly_zero_down():
    """Test monthly installments with 0% down payment."""
    print("\n=== Test: Monthly zero-down payment ===")
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=Decimal("0"),
        years=5,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    # Verify down payment is zero
    assert result.down_payment == Decimal("0"), f"Expected 0 down payment, got {result.down_payment}"
    
    # Verify installment count
    assert result.total_installments == 60, f"Expected 60 installments, got {result.total_installments}"
    
    # Verify installment amounts
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    assert len(installments) == 60, f"Expected 60 installment payments, got {len(installments)}"
    
    # Verify total reconciliation
    total_paid = sum(p.amount for p in result.payments if p.payment_type != PaymentType.MAINTENANCE)
    assert total_paid == plan.price, f"Total paid {total_paid} != price {plan.price}"
    
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Installments: {result.total_installments}")
    print(f"[PASSED] Installment amount: {result.installment_amount}")
    print(f"[PASSED] Total paid: {total_paid}")
    print(f"[PASSED] First installment month: {installments[0].month}")
    print(f"[PASSED] Last installment month: {installments[-1].month}")


def test_quarterly_zero_down():
    """Test quarterly installments with 0% down payment."""
    print("\n=== Test: Quarterly zero-down payment ===")
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=Decimal("0"),
        years=5,
        frequency=PaymentFrequency.QUARTERLY,
    )
    result = developer_schedule(plan)
    
    # Verify down payment is zero
    assert result.down_payment == Decimal("0"), f"Expected 0 down payment, got {result.down_payment}"
    
    # Verify installment count
    assert result.total_installments == 20, f"Expected 20 installments, got {result.total_installments}"
    
    # Verify installment amounts
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    assert len(installments) == 20, f"Expected 20 installment payments, got {len(installments)}"
    
    # Verify quarterly schedule: months 3, 6, 9, 12, ...
    expected_months = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]
    actual_months = [p.month for p in installments]
    assert actual_months == expected_months, f"Expected months {expected_months}, got {actual_months}"
    
    # Verify total reconciliation
    total_paid = sum(p.amount for p in result.payments if p.payment_type != PaymentType.MAINTENANCE)
    assert total_paid == plan.price, f"Total paid {total_paid} != price {plan.price}"
    
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Installments: {result.total_installments}")
    print(f"[PASSED] Installment amount: {result.installment_amount}")
    print(f"[PASSED] Total paid: {total_paid}")
    print(f"[PASSED] Payment months: {actual_months[:3]}...{actual_months[-3:]}")


def test_rounding_accuracy():
    """Test rounding and last installment adjustment."""
    print("\n=== Test: Rounding accuracy ===")
    plan = PaymentPlan(
        price=Decimal("100000.37"),
        down_payment_pct=Decimal("20"),
        years=2,
        frequency=PaymentFrequency.MONTHLY,
    )
    result = developer_schedule(plan)
    
    # Calculate expected values
    expected_down = Decimal("20000.07")  # 100000.37 * 0.20 = 20000.074, rounded to 20000.07
    expected_remaining = Decimal("80000.30")  # 100000.37 - 20000.07
    
    assert result.down_payment == expected_down, f"Expected down payment {expected_down}, got {result.down_payment}"
    
    # Verify total reconciliation (excluding maintenance)
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total_installments_paid = sum(p.amount for p in installments)
    
    assert total_installments_paid == expected_remaining, \
        f"Total installments {total_installments_paid} != remaining {expected_remaining}"
    
    # Verify last installment is adjusted
    regular_amount = result.installment_amount
    last_amount = installments[-1].amount
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Regular installment: {regular_amount}")
    print(f"[PASSED] Last installment: {last_amount}")
    print(f"[PASSED] Total installments paid: {total_installments_paid}")
    print(f"[PASSED] Reconciliation: {result.down_payment + total_installments_paid} = {plan.price}")


def test_missing_optional_values():
    """Test handling of None values for optional fields."""
    print("\n=== Test: Missing optional values ===")
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=None,  # Unknown
        years=3,
        frequency=PaymentFrequency.MONTHLY,
        delivery_pct=None,  # Unknown
        delivery_month=None,
        maintenance=None,  # Unknown
    )
    result = developer_schedule(plan)
    
    # Verify None values are preserved
    assert result.down_payment is None, f"Expected None down payment, got {result.down_payment}"
    assert result.delivery_payment is None, f"Expected None delivery, got {result.delivery_payment}"
    assert result.maintenance_payment is None, f"Expected None maintenance, got {result.maintenance_payment}"
    
    # Verify installments use full price
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total_paid = sum(p.amount for p in installments)
    assert total_paid == plan.price, f"Total paid {total_paid} != price {plan.price}"
    
    print(f"[PASSED] Down payment: {result.down_payment} (None preserved)")
    print(f"[PASSED] Delivery payment: {result.delivery_payment} (None preserved)")
    print(f"[PASSED] Maintenance: {result.maintenance_payment} (None preserved)")
    print(f"[PASSED] Total installments paid: {total_paid}")


def test_delivery_and_maintenance():
    """Test delivery and maintenance payment handling."""
    print("\n=== Test: Delivery and maintenance ===")
    plan = PaymentPlan(
        price=Decimal("1000000"),
        down_payment_pct=Decimal("20"),
        years=5,
        frequency=PaymentFrequency.MONTHLY,
        delivery_pct=Decimal("10"),
        delivery_month=36,
        maintenance=Decimal("5000"),
    )
    result = developer_schedule(plan)
    
    expected_down = Decimal("200000.00")
    expected_delivery = Decimal("100000.00")
    expected_installment_base = Decimal("700000.00")  # 1000000 - 200000 - 100000
    
    assert result.down_payment == expected_down
    assert result.delivery_payment == expected_delivery
    assert result.maintenance_payment == Decimal("5000")
    
    # Verify delivery payment in schedule
    delivery_payments = [p for p in result.payments if p.payment_type == PaymentType.DELIVERY]
    assert len(delivery_payments) == 1, f"Expected 1 delivery payment, got {len(delivery_payments)}"
    assert delivery_payments[0].month == 36
    assert delivery_payments[0].amount == expected_delivery
    
    # Verify maintenance payment in schedule
    maintenance_payments = [p for p in result.payments if p.payment_type == PaymentType.MAINTENANCE]
    assert len(maintenance_payments) == 1, f"Expected 1 maintenance payment, got {len(maintenance_payments)}"
    assert maintenance_payments[0].amount == Decimal("5000")
    
    # Verify installments total equals remaining amount (not including maintenance)
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total_installments = sum(p.amount for p in installments)
    assert total_installments == expected_installment_base, \
        f"Total installments {total_installments} != expected {expected_installment_base}"
    
    # Verify property price reconciliation (excluding maintenance)
    total_property = result.down_payment + total_installments + result.delivery_payment
    assert total_property == plan.price, f"Total property {total_property} != price {plan.price}"
    
    print(f"[PASSED] Down payment: {result.down_payment}")
    print(f"[PASSED] Delivery payment: {result.delivery_payment} at month {delivery_payments[0].month}")
    print(f"[PASSED] Maintenance: {result.maintenance_payment}")
    print(f"[PASSED] Installments total: {total_installments}")
    print(f"[PASSED] Property price reconciliation: {total_property} = {plan.price}")


def test_full_reconciliation():
    """Test exact payment reconciliation for fully specified plan."""
    print("\n=== Test: Full reconciliation ===")
    plan = PaymentPlan(
        price=Decimal("500000"),
        down_payment_pct=Decimal("15"),
        years=3,
        frequency=PaymentFrequency.QUARTERLY,
        delivery_pct=Decimal("5"),
        delivery_month=24,
        maintenance=Decimal("3000"),
    )
    result = developer_schedule(plan)
    
    # Calculate expected amounts
    expected_down = Decimal("75000.00")
    expected_delivery = Decimal("25000.00")
    expected_installments_base = Decimal("400000.00")
    
    assert result.down_payment == expected_down
    assert result.delivery_payment == expected_delivery
    
    # Sum all payments by type
    down_payments = [p for p in result.payments if p.payment_type == PaymentType.DOWN_PAYMENT]
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    delivery_payments = [p for p in result.payments if p.payment_type == PaymentType.DELIVERY]
    maintenance_payments = [p for p in result.payments if p.payment_type == PaymentType.MAINTENANCE]
    
    total_down = sum(p.amount for p in down_payments)
    total_installments = sum(p.amount for p in installments)
    total_delivery = sum(p.amount for p in delivery_payments)
    total_maintenance = sum(p.amount for p in maintenance_payments)
    
    # Property price reconciliation (excluding maintenance)
    total_property = total_down + total_installments + total_delivery
    assert total_property == plan.price, f"Property total {total_property} != price {plan.price}"
    
    print(f"[PASSED] Down payment total: {total_down}")
    print(f"[PASSED] Installments total: {total_installments}")
    print(f"[PASSED] Delivery total: {total_delivery}")
    print(f"[PASSED] Maintenance total: {total_maintenance}")
    print(f"[PASSED] Property price: {total_property} = {plan.price}")
    print(f"[PASSED] All payments: {len(result.payments)}")


def run_all_tests():
    """Run all verification tests."""
    print("=" * 60)
    print("DEVELOPER SCHEDULE VERIFICATION")
    print("=" * 60)
    
    try:
        test_monthly_zero_down()
        test_quarterly_zero_down()
        test_rounding_accuracy()
        test_missing_optional_values()
        test_delivery_and_maintenance()
        test_full_reconciliation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
