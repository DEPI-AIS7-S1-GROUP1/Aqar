"""
Financial data contracts for payment plan calculations.
"""
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaymentFrequency(str, Enum):
    """Payment frequency for installments."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class PaymentType(str, Enum):
    """Type of payment."""
    DOWN_PAYMENT = "down_payment"
    INSTALLMENT = "installment"
    DELIVERY = "delivery"
    MAINTENANCE = "maintenance"


class PaymentPlan(BaseModel):
    """Input payment plan specification."""
    price: Decimal = Field(..., description="Total property price")
    down_payment_pct: Optional[Decimal] = Field(None, description="Down payment percentage (0-100)")
    years: int = Field(..., description="Number of years for installments", gt=0)
    frequency: PaymentFrequency = Field(..., description="Payment frequency")
    delivery_pct: Optional[Decimal] = Field(None, description="Delivery payment percentage (0-100)")
    delivery_month: Optional[int] = Field(None, description="Delivery payment month", ge=1)
    maintenance: Optional[Decimal] = Field(None, description="Maintenance payment amount")


class MortgagePlan(BaseModel):
    """Input mortgage plan specification."""
    property_price: Decimal = Field(..., description="Total property price")
    down_payment: Decimal = Field(..., description="Down payment amount")
    annual_interest_rate: Decimal = Field(..., description="Annual interest rate as percentage (e.g., 15 for 15%)")
    years: int = Field(..., description="Loan duration in years", gt=0)


class Payment(BaseModel):
    """Individual payment in the schedule."""
    month: int = Field(..., description="Payment month (1-indexed)")
    amount: Decimal = Field(..., description="Payment amount")
    payment_type: PaymentType = Field(..., description="Type of payment")
    description: str = Field(..., description="Payment description")
    # Mortgage amortization details (optional)
    interest: Optional[Decimal] = Field(None, description="Interest portion of payment")
    principal: Optional[Decimal] = Field(None, description="Principal portion of payment")
    remaining_balance: Optional[Decimal] = Field(None, description="Remaining loan balance after payment")


class PlanResult(BaseModel):
    """Complete payment plan result."""
    payments: list[Payment] = Field(default_factory=list, description="List of all payments")
    total_price: Decimal = Field(..., description="Total property price")
    down_payment: Optional[Decimal] = Field(None, description="Down payment amount")
    delivery_payment: Optional[Decimal] = Field(None, description="Delivery payment amount")
    maintenance_payment: Optional[Decimal] = Field(None, description="Maintenance payment amount")
    installment_amount: Optional[Decimal] = Field(None, description="Regular installment amount")
    total_installments: Optional[int] = Field(None, description="Total number of installments")
    # Mortgage-specific fields
    loan_amount: Optional[Decimal] = Field(None, description="Financed loan amount")
    total_interest: Optional[Decimal] = Field(None, description="Total interest paid over loan term")
