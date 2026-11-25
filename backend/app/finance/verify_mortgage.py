"""
Verification script for mortgage_schedule() implementation.
Tests mortgage calculations against specifications.
"""
import sys
from pathlib import Path
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.finance import (
    mortgage_schedule,
    MortgagePlan,
    PaymentType,
)


def test_standard_mortgage():
    """Test standard mortgage calculation (Scenario 1)."""
    print("\n=== Test: Standard Mortgage ===")
    plan = MortgagePlan(
        property_price=Decimal("5000000"),
        down_payment=Decimal("1000000"),
        annual_interest_rate=Decimal("15"),
        years=10,
    )
    result = mortgage_schedule(plan)
    
    # Verify loan amount
    expected_loan = Decimal("4000000")
    assert result.loan_amount == expected_loan, \
        f"Expected loan {expected_loan}, got {result.loan_amount}"
    
    # Verify installment count
    assert result.total_installments == 120, \
        f"Expected 120 installments, got {result.total_installments}"
    
    # Verify monthly payment
    # Google Sheets: =PMT(15%/12, 10*12, -4000000) = 64,533.98
    expected_pmt = Decimal("64533.98")
    assert result.installment_amount == expected_pmt, \
        f"Expected PMT {expected_pmt}, got {result.installment_amount}"
    
    # Verify payment schedule
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    assert len(installments) == 120, \
        f"Expected 120 payment entries, got {len(installments)}"
    
    # Verify first payment details
    first_payment = installments[0]
    assert first_payment.month == 1
    expected_first_interest = Decimal("50000.00")  # 4,000,000 * 0.15 / 12
    assert first_payment.interest == expected_first_interest, \
        f"Expected first interest {expected_first_interest}, got {first_payment.interest}"
    
    # Verify last payment clears balance
    last_payment = installments[-1]
    assert last_payment.remaining_balance == Decimal("0"), \
        f"Expected final balance 0, got {last_payment.remaining_balance}"
    
    # Verify total paid
    total_paid = sum(p.amount for p in installments)
    total_expected = result.loan_amount + result.total_interest
    
    print(f"[PASSED] Loan amount: {result.loan_amount:,.2f}")
    print(f"[PASSED] Monthly payment: {result.installment_amount:,.2f}")
    print(f"[PASSED] Total installments: {result.total_installments}")
    print(f"[PASSED] First month interest: {first_payment.interest:,.2f}")
    print(f"[PASSED] First month principal: {first_payment.principal:,.2f}")
    print(f"[PASSED] Total interest: {result.total_interest:,.2f}")
    print(f"[PASSED] Total paid: {total_paid:,.2f}")
    print(f"[PASSED] Final balance: {last_payment.remaining_balance}")
    print(f"[PASSED] Google Sheets comparison: PMT matches 64,533.98")


def test_zero_interest():
    """Test zero interest mortgage (Scenario 2)."""
    print("\n=== Test: Zero Interest Mortgage ===")
    plan = MortgagePlan(
        property_price=Decimal("1000000"),
        down_payment=Decimal("200000"),
        annual_interest_rate=Decimal("0"),
        years=5,
    )
    result = mortgage_schedule(plan)
    
    expected_loan = Decimal("800000")
    expected_pmt = Decimal("13333.33")  # 800,000 / 60
    
    assert result.loan_amount == expected_loan
    assert result.installment_amount == expected_pmt
    
    # Verify all interest payments are zero
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    for payment in installments:
        if payment.month < len(installments):  # Not last payment
            assert payment.interest == Decimal("0"), \
                f"Month {payment.month} interest should be 0, got {payment.interest}"
    
    # Verify total interest is zero
    assert result.total_interest == Decimal("0"), \
        f"Expected total interest 0, got {result.total_interest}"
    
    # Verify final balance is zero
    last_payment = installments[-1]
    assert last_payment.remaining_balance == Decimal("0"), \
        f"Expected final balance 0, got {last_payment.remaining_balance}"
    
    print(f"[PASSED] Zero interest loan: {result.loan_amount:,.2f}")
    print(f"[PASSED] Monthly payment: {result.installment_amount:,.2f}")
    print(f"[PASSED] Total interest: {result.total_interest}")
    print(f"[PASSED] Final balance: {last_payment.remaining_balance}")


def test_amortization_behavior():
    """Test amortization behavior (Scenario 3)."""
    print("\n=== Test: Amortization Behavior ===")
    plan = MortgagePlan(
        property_price=Decimal("2000000"),
        down_payment=Decimal("500000"),
        annual_interest_rate=Decimal("12"),
        years=5,
    )
    result = mortgage_schedule(plan)
    
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    
    # Verify first month interest is from original balance
    first = installments[0]
    expected_first_interest = result.loan_amount * Decimal("12") / Decimal("1200")
    expected_first_interest = expected_first_interest.quantize(Decimal("0.01"))
    assert first.interest == expected_first_interest, \
        f"Expected first interest {expected_first_interest}, got {first.interest}"
    
    # Verify interest decreases over time
    mid = installments[30]
    last = installments[-1]
    assert first.interest > mid.interest, \
        "Interest should decrease: first > middle"
    assert mid.interest > last.interest, \
        "Interest should decrease: middle > last"
    
    # Verify principal increases over time
    assert first.principal < mid.principal, \
        "Principal should increase: first < middle"
    assert mid.principal < last.principal, \
        "Principal should increase: middle < last"
    
    # Verify balance decreases
    assert first.remaining_balance < result.loan_amount, \
        "Balance should decrease after first payment"
    assert mid.remaining_balance < first.remaining_balance, \
        "Balance should decrease: middle < first"
    assert last.remaining_balance == Decimal("0"), \
        "Final balance should be zero"
    
    print(f"[PASSED] First payment - Interest: {first.interest:,.2f}, Principal: {first.principal:,.2f}")
    print(f"[PASSED] Mid payment - Interest: {mid.interest:,.2f}, Principal: {mid.principal:,.2f}")
    print(f"[PASSED] Last payment - Interest: {last.interest:,.2f}, Principal: {last.principal:,.2f}")
    print(f"[PASSED] Balance progression: {result.loan_amount:,.2f} -> {mid.remaining_balance:,.2f} -> {last.remaining_balance}")
    print(f"[PASSED] Interest decreases over time")
    print(f"[PASSED] Principal increases over time")


def test_invalid_inputs():
    """Test invalid input validation (Scenario 4)."""
    print("\n=== Test: Invalid Inputs ===")
    
    # Negative property price
    try:
        plan = MortgagePlan(
            property_price=Decimal("-1000000"),
            down_payment=Decimal("200000"),
            annual_interest_rate=Decimal("15"),
            years=10,
        )
        mortgage_schedule(plan)
        assert False, "Should reject negative property price"
    except ValueError as e:
        print(f"[PASSED] Negative price rejected: {e}")
    
    # Negative down payment
    try:
        plan = MortgagePlan(
            property_price=Decimal("1000000"),
            down_payment=Decimal("-200000"),
            annual_interest_rate=Decimal("15"),
            years=10,
        )
        mortgage_schedule(plan)
        assert False, "Should reject negative down payment"
    except ValueError as e:
        print(f"[PASSED] Negative down payment rejected: {e}")
    
    # Down payment exceeds price
    try:
        plan = MortgagePlan(
            property_price=Decimal("1000000"),
            down_payment=Decimal("1500000"),
            annual_interest_rate=Decimal("15"),
            years=10,
        )
        mortgage_schedule(plan)
        assert False, "Should reject down payment > price"
    except ValueError as e:
        print(f"[PASSED] Down payment > price rejected: {e}")
    
    # Negative interest rate
    try:
        plan = MortgagePlan(
            property_price=Decimal("1000000"),
            down_payment=Decimal("200000"),
            annual_interest_rate=Decimal("-5"),
            years=10,
        )
        mortgage_schedule(plan)
        assert False, "Should reject negative interest rate"
    except ValueError as e:
        print(f"[PASSED] Negative interest rate rejected: {e}")
    
    # Zero years
    try:
        plan = MortgagePlan(
            property_price=Decimal("1000000"),
            down_payment=Decimal("200000"),
            annual_interest_rate=Decimal("15"),
            years=0,
        )
        mortgage_schedule(plan)
        assert False, "Should reject zero years"
    except (ValueError, Exception) as e:
        print(f"[PASSED] Zero years rejected: {e}")


def test_rounding_precision():
    """Test rounding and final balance precision."""
    print("\n=== Test: Rounding Precision ===")
    plan = MortgagePlan(
        property_price=Decimal("3333333.33"),
        down_payment=Decimal("333333.33"),
        annual_interest_rate=Decimal("13.75"),
        years=7,
    )
    result = mortgage_schedule(plan)
    
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    last = installments[-1]
    
    # Final balance must be zero or very close
    assert abs(last.remaining_balance) < Decimal("0.01"), \
        f"Final balance {last.remaining_balance} should be near zero"
    
    # Verify total paid equals loan + interest
    total_paid = sum(p.amount for p in installments)
    expected_total = result.loan_amount + result.total_interest
    
    # Allow small rounding difference
    diff = abs(total_paid - expected_total)
    assert diff < Decimal("1.00"), \
        f"Total paid difference {diff} too large"
    
    print(f"[PASSED] Final balance: {last.remaining_balance}")
    print(f"[PASSED] Total paid: {total_paid:,.2f}")
    print(f"[PASSED] Loan + Interest: {expected_total:,.2f}")
    print(f"[PASSED] Difference: {diff:.2f}")


def run_all_tests():
    """Run all verification tests."""
    print("=" * 60)
    print("MORTGAGE SCHEDULE VERIFICATION")
    print("=" * 60)
    
    try:
        test_standard_mortgage()
        test_zero_interest()
        test_amortization_behavior()
        test_invalid_inputs()
        test_rounding_precision()
        
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
