"""
Financial calculator for real estate payment plans.
"""
from decimal import Decimal, ROUND_HALF_UP

from backend.app.finance.contracts import (
    PaymentPlan,
    PlanResult,
    Payment,
    PaymentType,
    PaymentFrequency,
)


def developer_schedule(plan: PaymentPlan) -> PlanResult:
    """
    Calculate developer payment schedule with installments.
    
    This function generates a complete payment schedule based on the provided
    payment plan. It handles down payments, installments (monthly or quarterly),
    delivery payments, and maintenance fees.
    
    Args:
        plan: PaymentPlan specification with price, down payment, years, frequency,
              delivery terms, and maintenance.
    
    Returns:
        PlanResult with complete payment schedule and summary information.
    
    Raises:
        ValueError: If plan parameters are invalid or inconsistent.
    """
    # Validate inputs
    if plan.price <= 0:
        raise ValueError("Price must be positive")
    
    if plan.down_payment_pct is not None and (plan.down_payment_pct < 0 or plan.down_payment_pct > 100):
        raise ValueError("Down payment percentage must be between 0 and 100")
    
    if plan.delivery_pct is not None and (plan.delivery_pct < 0 or plan.delivery_pct > 100):
        raise ValueError("Delivery percentage must be between 0 and 100")
    
    if plan.delivery_month is not None and plan.delivery_month < 1:
        raise ValueError("Delivery month must be at least 1")
    
    if plan.maintenance is not None and plan.maintenance < 0:
        raise ValueError("Maintenance amount must be non-negative")
    
    # Calculate down payment
    down_payment = None
    if plan.down_payment_pct is not None:
        down_payment = (plan.price * plan.down_payment_pct / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    # Calculate delivery payment
    delivery_payment = None
    if plan.delivery_pct is not None:
        delivery_payment = (plan.price * plan.delivery_pct / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    # Calculate remaining amount for installments
    remaining = plan.price
    if down_payment is not None:
        remaining -= down_payment
    if delivery_payment is not None:
        remaining -= delivery_payment
    
    # Validate remaining amount
    if remaining < 0:
        raise ValueError("Down payment and delivery payment exceed property price")
    
    # Calculate installment count based on frequency
    if plan.frequency == PaymentFrequency.MONTHLY:
        num_installments = plan.years * 12
    elif plan.frequency == PaymentFrequency.QUARTERLY:
        num_installments = plan.years * 4
    else:
        raise ValueError(f"Unsupported payment frequency: {plan.frequency}")
    
    # Calculate installment amount
    installment_amount = None
    if num_installments > 0 and remaining > 0:
        base_installment = remaining / Decimal(num_installments)
        installment_amount = base_installment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Build payment schedule
    payments: list[Payment] = []
    
    # Add down payment
    if down_payment is not None and down_payment > 0:
        payments.append(
            Payment(
                month=0,
                amount=down_payment,
                payment_type=PaymentType.DOWN_PAYMENT,
                description="Down payment"
            )
        )
    
    # Add installments
    if installment_amount is not None and installment_amount > 0:
        total_installments_paid = Decimal("0")
        
        for i in range(num_installments):
            if plan.frequency == PaymentFrequency.MONTHLY:
                month = i + 1
            else:  # QUARTERLY
                month = (i + 1) * 3
            
            # Adjust last installment to account for rounding differences
            if i == num_installments - 1:
                amount = remaining - total_installments_paid
            else:
                amount = installment_amount
                total_installments_paid += amount
            
            payments.append(
                Payment(
                    month=month,
                    amount=amount,
                    payment_type=PaymentType.INSTALLMENT,
                    description=f"Installment {i + 1}/{num_installments}"
                )
            )
    
    # Add delivery payment
    if delivery_payment is not None and delivery_payment > 0:
        if plan.delivery_month is None:
            raise ValueError("Delivery month must be specified when delivery payment is set")
        
        payments.append(
            Payment(
                month=plan.delivery_month,
                amount=delivery_payment,
                payment_type=PaymentType.DELIVERY,
                description="Delivery payment"
            )
        )
    
    # Add maintenance payment
    if plan.maintenance is not None and plan.maintenance > 0:
        # Maintenance payment month is not specified in the contract
        # According to requirements, we cannot invent this
        # For now, we'll add it without a specific month (using 0 to indicate unspecified)
        payments.append(
            Payment(
                month=0,
                amount=plan.maintenance,
                payment_type=PaymentType.MAINTENANCE,
                description="Maintenance fee"
            )
        )
    
    # Sort payments by month (except maintenance which has month=0)
    payments.sort(key=lambda p: (p.month, p.payment_type.value))
    
    # Return result
    return PlanResult(
        payments=payments,
        total_price=plan.price,
        down_payment=down_payment,
        delivery_payment=delivery_payment,
        maintenance_payment=plan.maintenance,
        installment_amount=installment_amount,
        total_installments=num_installments if installment_amount is not None else None,
    )
