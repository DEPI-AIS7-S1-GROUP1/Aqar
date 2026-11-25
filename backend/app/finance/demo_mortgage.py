"""
Demonstration of mortgage_schedule() functionality.
Shows typical mortgage use cases and amortization details.
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


def demo_standard_mortgage():
    """Demonstrate standard mortgage with amortization."""
    print("\n" + "=" * 70)
    print("DEMO 1: Standard 10-Year Mortgage")
    print("=" * 70)
    
    plan = MortgagePlan(
        property_price=Decimal("5000000"),
        down_payment=Decimal("1000000"),
        annual_interest_rate=Decimal("15"),
        years=10,
    )
    
    result = mortgage_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.property_price:,.2f}")
    print(f"  Down Payment: EGP {plan.down_payment:,.2f}")
    print(f"  Annual Interest Rate: {plan.annual_interest_rate}%")
    print(f"  Duration: {plan.years} years")
    
    print(f"\nCalculated Mortgage:")
    print(f"  Loan Amount: EGP {result.loan_amount:,.2f}")
    print(f"  Monthly Payment: EGP {result.installment_amount:,.2f}")
    print(f"  Number of Payments: {result.total_installments}")
    print(f"  Total Interest: EGP {result.total_interest:,.2f}")
    print(f"  Total Amount Paid: EGP {result.loan_amount + result.total_interest:,.2f}")
    
    # Show first few payments
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    print(f"\nFirst 6 Monthly Payments:")
    print(f"  {'Month':<6} {'Payment':>14} {'Interest':>14} {'Principal':>14} {'Balance':>16}")
    print(f"  {'-'*6} {'-'*14} {'-'*14} {'-'*14} {'-'*16}")
    for payment in installments[:6]:
        print(f"  {payment.month:<6} "
              f"{payment.amount:>14,.2f} "
              f"{payment.interest:>14,.2f} "
              f"{payment.principal:>14,.2f} "
              f"{payment.remaining_balance:>16,.2f}")
    
    # Show last few payments
    print(f"\n  ... {result.total_installments - 12} payments omitted ...")
    print(f"\nLast 6 Monthly Payments:")
    print(f"  {'Month':<6} {'Payment':>14} {'Interest':>14} {'Principal':>14} {'Balance':>16}")
    print(f"  {'-'*6} {'-'*14} {'-'*14} {'-'*14} {'-'*16}")
    for payment in installments[-6:]:
        print(f"  {payment.month:<6} "
              f"{payment.amount:>14,.2f} "
              f"{payment.interest:>14,.2f} "
              f"{payment.principal:>14,.2f} "
              f"{payment.remaining_balance:>16,.2f}")


def demo_zero_interest():
    """Demonstrate zero-interest financing."""
    print("\n" + "=" * 70)
    print("DEMO 2: Zero-Interest Financing")
    print("=" * 70)
    
    plan = MortgagePlan(
        property_price=Decimal("1000000"),
        down_payment=Decimal("200000"),
        annual_interest_rate=Decimal("0"),
        years=5,
    )
    
    result = mortgage_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.property_price:,.2f}")
    print(f"  Down Payment: EGP {plan.down_payment:,.2f}")
    print(f"  Annual Interest Rate: {plan.annual_interest_rate}%")
    print(f"  Duration: {plan.years} years")
    
    print(f"\nCalculated Plan:")
    print(f"  Loan Amount: EGP {result.loan_amount:,.2f}")
    print(f"  Monthly Payment: EGP {result.installment_amount:,.2f}")
    print(f"  Number of Payments: {result.total_installments}")
    print(f"  Total Interest: EGP {result.total_interest:,.2f}")
    
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    print(f"\nSample Payments:")
    print(f"  {'Month':<6} {'Payment':>14} {'Interest':>14} {'Principal':>14} {'Balance':>16}")
    print(f"  {'-'*6} {'-'*14} {'-'*14} {'-'*14} {'-'*16}")
    for i in [0, 29, 59]:
        payment = installments[i]
        print(f"  {payment.month:<6} "
              f"{payment.amount:>14,.2f} "
              f"{payment.interest:>14,.2f} "
              f"{payment.principal:>14,.2f} "
              f"{payment.remaining_balance:>16,.2f}")


def demo_comparison():
    """Compare different mortgage terms."""
    print("\n" + "=" * 70)
    print("DEMO 3: Mortgage Term Comparison")
    print("=" * 70)
    
    base_price = Decimal("2000000")
    base_down = Decimal("400000")
    base_rate = Decimal("12")
    
    terms = [5, 10, 15, 20]
    
    print(f"\nProperty: EGP {base_price:,.2f}")
    print(f"Down Payment: EGP {base_down:,.2f}")
    print(f"Interest Rate: {base_rate}%")
    print(f"\nComparison:")
    print(f"  {'Term':<8} {'Monthly Pmt':>14} {'Total Interest':>16} {'Total Paid':>16}")
    print(f"  {'-'*8} {'-'*14} {'-'*16} {'-'*16}")
    
    for years in terms:
        plan = MortgagePlan(
            property_price=base_price,
            down_payment=base_down,
            annual_interest_rate=base_rate,
            years=years,
        )
        result = mortgage_schedule(plan)
        total_paid = result.loan_amount + result.total_interest
        
        print(f"  {years} years "
              f"{result.installment_amount:>14,.2f} "
              f"{result.total_interest:>16,.2f} "
              f"{total_paid:>16,.2f}")


def demo_amortization_progression():
    """Show how principal and interest change over time."""
    print("\n" + "=" * 70)
    print("DEMO 4: Amortization Progression")
    print("=" * 70)
    
    plan = MortgagePlan(
        property_price=Decimal("3000000"),
        down_payment=Decimal("600000"),
        annual_interest_rate=Decimal("14"),
        years=15,
    )
    
    result = mortgage_schedule(plan)
    
    print(f"\nMortgage: EGP {result.loan_amount:,.2f} at {plan.annual_interest_rate}% for {plan.years} years")
    print(f"Monthly Payment: EGP {result.installment_amount:,.2f}")
    
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    
    # Show yearly progression
    print(f"\nYearly Breakdown:")
    print(f"  {'Year':<6} {'Interest Paid':>16} {'Principal Paid':>16} {'End Balance':>16}")
    print(f"  {'-'*6} {'-'*16} {'-'*16} {'-'*16}")
    
    for year in range(1, plan.years + 1):
        start_month = (year - 1) * 12
        end_month = year * 12
        year_payments = installments[start_month:end_month]
        
        year_interest = sum(p.interest for p in year_payments)
        year_principal = sum(p.principal for p in year_payments)
        end_balance = year_payments[-1].remaining_balance if year_payments else Decimal("0")
        
        print(f"  {year:<6} "
              f"{year_interest:>16,.2f} "
              f"{year_principal:>16,.2f} "
              f"{end_balance:>16,.2f}")
    
    print(f"\nNote: Interest payments decrease while principal payments increase over time.")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MORTGAGE SCHEDULE DEMONSTRATIONS")
    print("=" * 70)
    
    demo_standard_mortgage()
    demo_zero_interest()
    demo_comparison()
    demo_amortization_progression()
    
    print("\n" + "=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print()
