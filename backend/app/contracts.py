"""AqarAI shared Pydantic models and contracts."""

import math
from datetime import datetime
from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field, model_validator

# ---- lead models (Manal) ----
# S0-T3-2. Source: AqarAI-Architecture.docx, sections "LeadState", "Handoff protocol", "LeadBrief".
# RULE: unknown = None, never 0.  (0 means the customer really said zero.)

T = TypeVar("T")


class Mode(str, Enum):
    """Who is talking to the customer right now (the handoff state machine)."""
    AI_ACTIVE = "AI_ACTIVE"
    HANDOFF_PENDING = "HANDOFF_PENDING"
    HUMAN_ACTIVE = "HUMAN_ACTIVE"
    CLOSED = "CLOSED"


class Band(str, Enum):
    """Score label. Cold < 40, Warm 40-69, Hot >= 70."""
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class Intent(str, Enum):
    """What the customer wants in this message (output of the extract node)."""
    SEARCH = "search"
    INFO = "info"
    COMPARE = "compare"
    VISIT_OR_RESERVE = "visit_or_reserve"
    HUMAN_REQUEST = "human_request"
    OBJECTION = "objection"
    OFF_TOPIC = "off_topic"


Timeline = Literal["0-3m", "3-12m", "12m+", "unknown"]
Purpose = Literal["live", "invest"]


class Slot(BaseModel, Generic[T]):
    """One piece of information plus whether the customer confirmed it.
    The score only counts slots with confirmed=True."""
    value: T | None = None
    confirmed: bool = False


class SlotPatch(BaseModel):
    """ONLY what the customer said in the latest message. Every field optional.
    This is what the extract node (LLM) returns."""
    areas: list[str] | None = None              # canonical ids, e.g. "new_cairo"
    down_payment_available_egp: float | None = None
    monthly_capacity_egp: float | None = None
    budget_total_egp: float | None = None
    timeline: Timeline | None = None
    purpose: Purpose | None = None
    unit_type: str | None = None
    bedrooms_min: int | None = None
    intent: Intent | None = None


class Slots(BaseModel):
    """Everything we know so far, each value with its confirmed flag."""
    areas: Slot[list[str]] = Field(default_factory=Slot)
    down_payment_available_egp: Slot[float] = Field(default_factory=Slot)
    monthly_capacity_egp: Slot[float] = Field(default_factory=Slot)
    budget_total_egp: Slot[float] = Field(default_factory=Slot)
    timeline: Slot[Timeline] = Field(default_factory=Slot)
    purpose: Slot[Purpose] = Field(default_factory=Slot)
    unit_type: Slot[str] = Field(default_factory=Slot)
    bedrooms_min: Slot[int] = Field(default_factory=Slot)


class Feedback(BaseModel):
    listing_id: str
    reaction: Literal["liked", "rejected"]
    reason: str | None = None


class AffordabilityEntry(BaseModel):
    """Affordability of ONE plan for THIS customer, stored on the lead."""
    listing_id: str
    plan_id: str
    status: Literal["fit", "tight", "not_fit", "unknown"]
    flags: list[str] = []                          # e.g. ["delivery_payment"]


class Score(BaseModel):
    value: int = 0
    band: Band = Band.COLD
    reasons: list[str] = []


class HandoffInfo(BaseModel):
    trigger: str | None = None                  # None until a handoff happens
    at: datetime | None = None


class Failures(BaseModel):
    extraction_retries: int = 0
    guard_rejections: int = 0
    off_topic_turns: int = 0


class LeadState(BaseModel):
    """The whole memory of one conversation. LangGraph carries this."""
    conversation_id: str
    lead_id: str
    mode: Mode = Mode.AI_ACTIVE
    slots: Slots = Field(default_factory=Slots)
    contact_consent: bool = False
    shown_listing_ids: list[str] = []
    feedback: list[Feedback] = []
    affordability: list[AffordabilityEntry] = []
    score: Score = Field(default_factory=Score)
    handoff: HandoffInfo = Field(default_factory=HandoffInfo)
    failures: Failures = Field(default_factory=Failures)


class MatchedUnit(BaseModel):
    listing_id: str
    plan_id: str
    affordability: Literal["fit", "tight", "not_fit", "unknown"]
    liked: bool | None = None                   # None = customer gave no opinion


class ConfirmedSlots(BaseModel):
    """Only the values the customer confirmed. Unconfirmed ones go in LeadBrief.unconfirmed."""
    areas: list[str] | None = None
    down_payment_available_egp: float | None = None
    monthly_capacity_egp: float | None = None
    timeline: Timeline | None = None
    purpose: Purpose | None = None


class LeadBrief(BaseModel):
    """What the broker reads when the AI hands over."""
    lead_id: str
    trigger: str                                   # why the handoff happened
    band: Band
    score: int
    reasons: list[str] = []
    confirmed: ConfirmedSlots = Field(default_factory=ConfirmedSlots)
    unconfirmed: list[str] = []                    # slot names, e.g. ["bedrooms_min"]
    matched_units: list[MatchedUnit] = []
    open_questions: list[str] = []
    summary_text: str | None = None             # 60-80 words, checked by the honesty rule
    transcript_url: str | None = None

# ---- listing and search models (Member 3) ----
"""Pydantic models for property listings and payment plans.
All optional fields default to ``None``; unknown values must be ``None`` (never ``0``).
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

# NOTE: optional fields default to None; never use 0 for unknown values.

class Listing(BaseModel):
    # S0-T3-4: optional for now so existing rows/examples still load.
    # TODO(S1-T2-1): make required once the listings table defines the id.
    listing_id: str | None = None
    source_url: str
    collected_at: datetime
    collected_by: str
    verified_by: str | None = None
    area: str
    developer: str
    price_egp: float
    area_sqm: float
    delivery_date: date | None = None
    down_payment_pct: float
    years: int
    frequency: Literal["monthly", "quarterly"]
    delivery_payment_pct: float | None = None
    maintenance_pct: float | None = None
    notes: str | None = None

class PaymentPlan(BaseModel):
    """One developer payment plan as published by the source. Extended in S0-T3-4.

    The down payment is stored in EGP when the source gives an amount.
    ``down_payment_source`` says which value came from the source; the other one
    is computed by the data loader from ``Listing.price_egp`` (this model has no price).
    Reconciling an amount that disagrees with a percent is the loader's job, not this model's.
    Unknown values are ``None``; ``0`` is a real zero (e.g. a 0% down payment).
    """
    plan_id: str
    down_payment_egp: float | None = Field(default=None, ge=0)
    down_payment_pct: float | None = Field(default=None, ge=0, le=100)
    down_payment_source: Literal["egp", "pct"] | None = None   # None only if both are unknown
    years: int = Field(ge=0)
    frequency: Literal["monthly", "quarterly"]
    delivery_payment_pct: float | None = Field(default=None, ge=0, le=100)
    delivery_month: int | None = Field(default=None, ge=0)      # months after contract
    maintenance_pct: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _check_down_payment(self) -> "PaymentPlan":
        if self.down_payment_source == "egp" and self.down_payment_egp is None:
            raise ValueError("down_payment_source='egp' but down_payment_egp is None")
        if self.down_payment_source == "pct" and self.down_payment_pct is None:
            raise ValueError("down_payment_source='pct' but down_payment_pct is None")
        has_value = self.down_payment_egp is not None or self.down_payment_pct is not None
        if self.down_payment_source is None and has_value:
            raise ValueError("down_payment_source is required when a down payment value is set")
        if (
            self.down_payment_pct is not None
            and self.delivery_payment_pct is not None
            and self.down_payment_pct + self.delivery_payment_pct > 100
        ):
            raise ValueError("down_payment_pct + delivery_payment_pct is more than 100")
        return self

class SearchQuery(BaseModel):
    area: str | None = None
    developer: str | None = None
    min_price_egp: float | None = None
    max_price_egp: float | None = None
    frequency: Literal["monthly", "quarterly"] | None = None

class SearchResult(BaseModel):
    total: int
    results: list[Listing]


# ---- calculator and affordability result models (Member 4) ----
# S0-T3-4. Every number in these models is produced by code (calculator / affordability
# tools), never by the LLM. Unknown = None, never 0. Use `is None` checks, not `if not x`.

AffordabilityStatus = Literal["fit", "tight", "not_fit", "unknown"]

# Float noise allowance in EGP when checking sums computed by code. Not a data tolerance.
_EGP_ABS_TOL = 0.01


class PlanResult(BaseModel):
    """Calculator output for ONE plan of ONE listing (S1-T3-1 / S1-T3-2). npv() (S1-T3-3) reads it.

    ``delivery_payment_egp=None`` means the source did not publish it (unknown), and a
    ``"delivery_payment_unknown"`` warning is added. ``0.0`` means the plan really has none.
    """
    listing_id: str
    plan_id: str
    plan_type: Literal["developer", "bank"]
    price_egp: float = Field(gt=0)
    down_payment_egp: float = Field(ge=0)
    down_payment_pct: float = Field(ge=0, le=100)
    delivery_payment_egp: float | None = Field(default=None, ge=0)
    delivery_month: int | None = Field(default=None, ge=0)
    installment_count: int = Field(ge=0)
    installment_egp: float = Field(ge=0)            # 0 when the down payment is 100%
    monthly_equivalent_egp: float = Field(ge=0)     # quarterly: installment / 3
    total_paid_egp: float = Field(ge=0)
    npv_egp: float | None = Field(default=None, ge=0)
    annual_discount_rate_pct: float | None = Field(default=None, ge=0)
    warnings: list[str] = []

    @model_validator(mode="after")
    def _check_amounts(self) -> "PlanResult":
        delivery = self.delivery_payment_egp
        upfront = self.down_payment_egp + (0.0 if delivery is None else delivery)
        if upfront > self.price_egp + _EGP_ABS_TOL:
            raise ValueError("down payment + delivery payment is more than price_egp")

        if self.installment_count == 0:
            if self.installment_egp > _EGP_ABS_TOL or self.monthly_equivalent_egp > _EGP_ABS_TOL:
                raise ValueError("installment_count is 0 but an installment amount is set")
            if delivery is not None and self.price_egp - upfront > _EGP_ABS_TOL:
                raise ValueError("installment_count is 0 but part of the price is left unpaid")

        if (self.npv_egp is None) != (self.annual_discount_rate_pct is None):
            raise ValueError("npv_egp and annual_discount_rate_pct must be set together")

        if (
            self.plan_type == "developer"
            and delivery is None
            and "delivery_payment_unknown" not in self.warnings
        ):
            self.warnings.append("delivery_payment_unknown")
        if (
            delivery is not None
            and delivery > 0
            and self.delivery_month is None
            and "delivery_month_unknown" not in self.warnings
        ):
            self.warnings.append("delivery_month_unknown")
        return self


class AffordabilityResult(BaseModel):
    """Can THIS customer afford ONE plan? Output of the affordability tool (S1-T6-1).

    Gaps are ``required - available``: positive = shortfall, zero or negative = covered.
    The fit / tight thresholds live in the affordability code, not here.
    """
    listing_id: str
    plan_id: str
    status: AffordabilityStatus
    down_payment_required_egp: float | None = Field(default=None, ge=0)
    down_payment_available_egp: float | None = Field(default=None, ge=0)
    down_payment_gap_egp: float | None = None
    monthly_required_egp: float | None = Field(default=None, ge=0)
    monthly_capacity_egp: float | None = Field(default=None, ge=0)
    monthly_gap_egp: float | None = None
    flags: list[str] = []                          # e.g. ["delivery_payment"]
    missing_inputs: list[str] = []                 # e.g. ["monthly_capacity_egp"]

    @model_validator(mode="after")
    def _check_status(self) -> "AffordabilityResult":
        pairs = (
            ("down_payment", self.down_payment_required_egp,
             self.down_payment_available_egp, self.down_payment_gap_egp),
            ("monthly", self.monthly_required_egp,
             self.monthly_capacity_egp, self.monthly_gap_egp),
        )
        for name, required, available, gap in pairs:
            if gap is None:
                continue
            if required is None or available is None:
                raise ValueError(f"{name} gap is set but one of its inputs is None")
            if not math.isclose(gap, required - available, abs_tol=_EGP_ABS_TOL):
                raise ValueError(f"{name} gap must equal required - available")

        if self.status == "unknown":
            if not self.missing_inputs:
                raise ValueError("status='unknown' needs at least one missing_inputs entry")
        else:
            if self.missing_inputs:
                raise ValueError(f"status='{self.status}' cannot have missing_inputs")
            if self.down_payment_gap_egp is None or self.monthly_gap_egp is None:
                raise ValueError(f"status='{self.status}' needs both gaps to be known")
        return self

    def to_entry(self) -> AffordabilityEntry:
        """The short form stored on LeadState.affordability."""
        return AffordabilityEntry(
            listing_id=self.listing_id,
            plan_id=self.plan_id,
            status=self.status,
            flags=list(self.flags),
        )
