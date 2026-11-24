"""AqarAI shared Pydantic models and contracts."""

from datetime import datetime
from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

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
    down_payment_pct: float
    years: int
    frequency: Literal["monthly", "quarterly"]
    delivery_payment_pct: float | None = None
    maintenance_pct: float | None = None

class SearchQuery(BaseModel):
    area: str | None = None
    developer: str | None = None
    min_price_egp: float | None = None
    max_price_egp: float | None = None
    frequency: Literal["monthly", "quarterly"] | None = None

class SearchResult(BaseModel):
    total: int
    results: list[Listing]

