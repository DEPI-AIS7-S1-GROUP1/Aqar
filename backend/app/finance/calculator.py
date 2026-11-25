"""
Financial calculator for real estate payment plans.
"""
from decimal import Decimal, ROUND_HALF_UP

from backend.app.finance.contracts import (
    PaymentPlan,
    MortgagePlan,
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


def mortgage_schedule(plan: MortgagePlan) -> PlanResult:
    """
    Calculate mortgage amortization schedule with monthly installments.
    
    This function generates a complete mortgage payment schedule based on
    standard amortization formulas. It calculates the fixed monthly payment
    (PMT) and provides detailed breakdown of interest, principal, and
    remaining balance for each month.
    
    Args:
        plan: MortgagePlan specification with property price, down payment,
              annual interest rate, and loan duration in years.
    
    Returns:
        PlanResult with complete amortization schedule and summary information.
    
    Raises:
        ValueError: If plan parameters are invalid or inconsistent.
    """
    # Validate inputs
    if plan.property_price <= 0:
        raise ValueError("Property price must be positive")
    
    if plan.down_payment < 0:
        raise ValueError("Down payment must be non-negative")
    
    if plan.down_payment > plan.property_price:
        raise ValueError("Down payment cannot exceed property price")
    
    if plan.annual_interest_rate < 0:
        raise ValueError("Annual interest rate must be non-negative")
    
    if plan.years <= 0:
        raise ValueError("Loan duration must be positive")
    
    # Calculate loan amount
    loan_amount = plan.property_price - plan.down_payment
    
    if loan_amount <= 0:
        raise ValueError("Loan amount must be positive (down payment cannot equal or exceed property price)")
    
    # Calculate number of monthly installments
    num_installments = plan.years * 12
    
    # Convert annual interest rate (percentage) to monthly rate (decimal)
    # e.g., 15% annual -> 15/12 = 1.25% monthly -> 0.0125 as decimal
    monthly_rate = plan.annual_interest_rate / Decimal("12") / Decimal("100")
    
    # Calculate monthly payment using PMT formula
    if monthly_rate == 0:
        # Zero interest case: simple division
        monthly_payment = loan_amount / Decimal(num_installments)
    else:
        # Standard PMT formula: PMT = P * r / (1 - (1 + r)^-n)
        # where P = loan amount, r = monthly rate, n = number of payments
        rate_plus_one = Decimal("1") + monthly_rate
        denominator = Decimal("1") - (rate_plus_one ** (-num_installments))
        monthly_payment = loan_amount * monthly_rate / denominator
    
    # Round monthly payment to 2 decimal places
    monthly_payment = monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # Build amortization schedule
    payments: list[Payment] = []
    remaining_balance = loan_amount
    total_interest_paid = Decimal("0")
    
    # Add down payment if greater than zero
    if plan.down_payment > 0:
        payments.append(
            Payment(
                month=0,
                amount=plan.down_payment,
                payment_type=PaymentType.DOWN_PAYMENT,
                description="Down payment",
                interest=None,
                principal=None,
                remaining_balance=None,
            )
        )
    
    # Generate monthly amortization schedule
    for month_num in range(1, num_installments + 1):
        # Calculate interest for this month
        interest_payment = (remaining_balance * monthly_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Calculate principal payment
        principal_payment = monthly_payment - interest_payment
        
        # For the last payment, adjust to clear remaining balance
        if month_num == num_installments:
            # Adjust principal to exactly clear the loan
            principal_payment = remaining_balance
            # Recalculate total payment for last month
            actual_payment = interest_payment + principal_payment
        else:
            actual_payment = monthly_payment
        
        # Update remaining balance
        new_balance = remaining_balance - principal_payment
        
        # Ensure balance doesn't go negative due to rounding
        if new_balance < 0:
            new_balance = Decimal("0")
        
        # Track total interest
        total_interest_paid += interest_payment
        
        # Add payment to schedule
        payments.append(
            Payment(
                month=month_num,
                amount=actual_payment,
                payment_type=PaymentType.INSTALLMENT,
                description=f"Mortgage payment {month_num}/{num_installments}",
                interest=interest_payment,
                principal=principal_payment,
                remaining_balance=new_balance,
            )
        )
        
        # Update balance for next iteration
        remaining_balance = new_balance
    
    # Return result
    return PlanResult(
        payments=payments,
        total_price=plan.property_price,
        down_payment=plan.down_payment if plan.down_payment > 0 else None,
        delivery_payment=None,
        maintenance_payment=None,
        installment_amount=monthly_payment,
        total_installments=num_installments,
        loan_amount=loan_amount,
        total_interest=total_interest_paid,
    )
