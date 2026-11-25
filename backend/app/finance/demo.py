"""
Demonstration of developer_schedule() functionality.
Shows typical use cases and output format.
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


def demo_basic_monthly():
    """Demonstrate basic monthly payment plan."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Monthly Payment Plan")
    print("=" * 70)
    
    plan = PaymentPlan(
        price=Decimal("500000"),
        down_payment_pct=Decimal("20"),
        years=3,
        frequency=PaymentFrequency.MONTHLY,
    )
    
    result = developer_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.price:,.2f}")
    print(f"  Down Payment: {plan.down_payment_pct}%")
    print(f"  Duration: {plan.years} years")
    print(f"  Frequency: {plan.frequency.value}")
    
    print(f"\nCalculated Plan:")
    print(f"  Down Payment: EGP {result.down_payment:,.2f}")
    print(f"  Monthly Installment: EGP {result.installment_amount:,.2f}")
    print(f"  Number of Installments: {result.total_installments}")
    print(f"  Total Payments: {len(result.payments)}")
    
    print(f"\nFirst 5 Payments:")
    for payment in result.payments[:5]:
        print(f"  Month {payment.month:2d}: EGP {payment.amount:>12,.2f} - {payment.description}")
    
    print(f"\n  ... {result.total_installments - 5} more installments ...")


def demo_quarterly_with_delivery():
    """Demonstrate quarterly plan with delivery payment."""
    print("\n" + "=" * 70)
    print("DEMO 2: Quarterly Plan with Delivery Payment")
    print("=" * 70)
    
    plan = PaymentPlan(
        price=Decimal("1200000"),
        down_payment_pct=Decimal("15"),
        years=5,
        frequency=PaymentFrequency.QUARTERLY,
        delivery_pct=Decimal("10"),
        delivery_month=48,
    )
    
    result = developer_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.price:,.2f}")
    print(f"  Down Payment: {plan.down_payment_pct}%")
    print(f"  Delivery Payment: {plan.delivery_pct}% at month {plan.delivery_month}")
    print(f"  Duration: {plan.years} years")
    print(f"  Frequency: {plan.frequency.value}")
    
    print(f"\nCalculated Plan:")
    print(f"  Down Payment: EGP {result.down_payment:,.2f}")
    print(f"  Quarterly Installment: EGP {result.installment_amount:,.2f}")
    print(f"  Delivery Payment: EGP {result.delivery_payment:,.2f}")
    print(f"  Number of Installments: {result.total_installments}")
    
    # Show payment breakdown by type
    down_payments = [p for p in result.payments if p.payment_type == PaymentType.DOWN_PAYMENT]
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    delivery_payments = [p for p in result.payments if p.payment_type == PaymentType.DELIVERY]
    
    print(f"\nPayment Breakdown:")
    if down_payments:
        print(f"  Down Payment: {len(down_payments)} payment(s)")
    print(f"  Installments: {len(installments)} payments")
    if delivery_payments:
        print(f"  Delivery: {len(delivery_payments)} payment(s) at month {delivery_payments[0].month}")
    
    print(f"\nSample Quarterly Schedule:")
    for payment in installments[:6]:
        print(f"  Month {payment.month:2d}: EGP {payment.amount:>12,.2f} - {payment.description}")


def demo_complete_plan():
    """Demonstrate complete plan with all payment types."""
    print("\n" + "=" * 70)
    print("DEMO 3: Complete Plan (All Payment Types)")
    print("=" * 70)
    
    plan = PaymentPlan(
        price=Decimal("800000"),
        down_payment_pct=Decimal("25"),
        years=4,
        frequency=PaymentFrequency.MONTHLY,
        delivery_pct=Decimal("5"),
        delivery_month=36,
        maintenance=Decimal("3500"),
    )
    
    result = developer_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.price:,.2f}")
    print(f"  Down Payment: {plan.down_payment_pct}%")
    print(f"  Delivery Payment: {plan.delivery_pct}% at month {plan.delivery_month}")
    print(f"  Maintenance Fee: EGP {plan.maintenance:,.2f}")
    print(f"  Duration: {plan.years} years")
    print(f"  Frequency: {plan.frequency.value}")
    
    print(f"\nCalculated Plan:")
    print(f"  Down Payment: EGP {result.down_payment:,.2f}")
    print(f"  Monthly Installment: EGP {result.installment_amount:,.2f}")
    print(f"  Delivery Payment: EGP {result.delivery_payment:,.2f}")
    print(f"  Maintenance: EGP {result.maintenance_payment:,.2f}")
    
    # Payment breakdown
    by_type = {}
    total_by_type = {}
    for payment in result.payments:
        ptype = payment.payment_type
        by_type[ptype] = by_type.get(ptype, 0) + 1
        total_by_type[ptype] = total_by_type.get(ptype, Decimal("0")) + payment.amount
    
    print(f"\nPayment Summary:")
    for ptype in [PaymentType.DOWN_PAYMENT, PaymentType.INSTALLMENT, 
                  PaymentType.DELIVERY, PaymentType.MAINTENANCE]:
        if ptype in by_type:
            count = by_type[ptype]
            total = total_by_type[ptype]
            print(f"  {ptype.value.replace('_', ' ').title()}: "
                  f"{count} payment(s) = EGP {total:,.2f}")
    
    # Verify reconciliation
    property_total = (
        result.down_payment +
        sum(p.amount for p in result.payments if p.payment_type == PaymentType.INSTALLMENT) +
        result.delivery_payment
    )
    
    print(f"\nReconciliation:")
    print(f"  Property components: EGP {property_total:,.2f}")
    print(f"  Property price: EGP {plan.price:,.2f}")
    print(f"  Match: {'[PASS]' if property_total == plan.price else '[FAIL]'}")
    print(f"  (Maintenance excluded from property price)")


def demo_zero_down():
    """Demonstrate zero down payment plan."""
    print("\n" + "=" * 70)
    print("DEMO 4: Zero Down Payment Plan")
    print("=" * 70)
    
    plan = PaymentPlan(
        price=Decimal("600000"),
        down_payment_pct=Decimal("0"),
        years=6,
        frequency=PaymentFrequency.MONTHLY,
    )
    
    result = developer_schedule(plan)
    
    print(f"\nInput:")
    print(f"  Property Price: EGP {plan.price:,.2f}")
    print(f"  Down Payment: {plan.down_payment_pct}% (zero down)")
    print(f"  Duration: {plan.years} years")
    print(f"  Frequency: {plan.frequency.value}")
    
    print(f"\nCalculated Plan:")
    print(f"  Down Payment: EGP {result.down_payment:,.2f}")
    print(f"  Monthly Installment: EGP {result.installment_amount:,.2f}")
    print(f"  Number of Installments: {result.total_installments}")
    
    # Verify full price covered by installments
    installments = [p for p in result.payments if p.payment_type == PaymentType.INSTALLMENT]
    total = sum(p.amount for p in installments)
    
    print(f"\nNote: With 0% down, installments cover full property price")
    print(f"  Total from installments: EGP {total:,.2f}")
    print(f"  Property price: EGP {plan.price:,.2f}")
    print(f"  Match: {'[PASS]' if total == plan.price else '[FAIL]'}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DEVELOPER SCHEDULE DEMONSTRATIONS")
    print("=" * 70)
    
    demo_basic_monthly()
    demo_quarterly_with_delivery()
    demo_complete_plan()
    demo_zero_down()
    
    print("\n" + "=" * 70)
    print("All demonstrations completed successfully!")
    print("=" * 70)
    print()
