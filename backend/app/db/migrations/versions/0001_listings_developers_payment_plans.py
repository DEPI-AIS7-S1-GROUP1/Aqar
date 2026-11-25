"""S1-T2-1 create developers, listings and payment_plans

Columns follow ``Listing`` and ``PaymentPlan`` in app/contracts.py (S0-T3-4 version).
Rules:
* An optional contract field is a nullable column with no server default.
  Unknown is NULL, never 0.
* A required contract field is NOT NULL.
* Money is EGP in NUMERIC(14, 2); percentages are NUMERIC(6, 3). No floats in the database.
* CHECK constraints copy the contract's bounds so bad rows fail in the database too.

Revision ID: 0001
Revises:
Create Date: 2026-11-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

EGP = sa.Numeric(14, 2)
PCT = sa.Numeric(6, 3)
FREQUENCY_CHECK = "frequency IN ('monthly', 'quarterly')"


def upgrade() -> None:
    op.create_table(
        "developers",
        sa.Column("developer_id", sa.BigInteger, sa.Identity(), primary_key=True),
        # Same text as Listing.developer, so listings can reference it by name.
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_table(
        "listings",
        # Contract field is optional until the ingest assigns ids (TODO S1-T2-1 in
        # contracts.py); the database needs a key, so it is required here.
        sa.Column("listing_id", sa.Text, primary_key=True),
        sa.Column("source_url", sa.Text, nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collected_by", sa.Text, nullable=False),
        sa.Column("verified_by", sa.Text, nullable=True),
        sa.Column("area", sa.Text, nullable=False),
        sa.Column("developer", sa.Text,
                  sa.ForeignKey("developers.name", onupdate="CASCADE", ondelete="RESTRICT"),
                  nullable=False),
        sa.Column("price_egp", EGP, nullable=False),
        sa.Column("area_sqm", sa.Numeric(10, 2), nullable=False),
        sa.Column("delivery_date", sa.Date, nullable=True),
        sa.Column("down_payment_pct", PCT, nullable=False),
        sa.Column("years", sa.Integer, nullable=False),
        sa.Column("frequency", sa.Text, nullable=False),
        sa.Column("delivery_payment_pct", PCT, nullable=True),
        sa.Column("maintenance_pct", PCT, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Helper columns (task sheet step 4). Not in the contract.
        # missing_fields: names of fields the source did not publish. Empty list = none missing.
        sa.Column("missing_fields", sa.ARRAY(sa.Text), nullable=False,
                  server_default=sa.text("'{}'::text[]")),
        # data_version: which data drop the row came from. NULL = not recorded.
        sa.Column("data_version", sa.Text, nullable=True),
        sa.CheckConstraint("price_egp > 0", name="ck_listings_price_positive"),
        sa.CheckConstraint("area_sqm > 0", name="ck_listings_area_positive"),
        sa.CheckConstraint("down_payment_pct BETWEEN 0 AND 100",
                           name="ck_listings_down_payment_pct"),
        sa.CheckConstraint("years >= 0", name="ck_listings_years"),
        sa.CheckConstraint(FREQUENCY_CHECK, name="ck_listings_frequency"),
        sa.CheckConstraint("delivery_payment_pct BETWEEN 0 AND 100",
                           name="ck_listings_delivery_payment_pct"),
        sa.CheckConstraint("maintenance_pct >= 0", name="ck_listings_maintenance_pct"),
    )
    op.create_index("ix_listings_area", "listings", ["area"])
    op.create_index("ix_listings_price_egp", "listings", ["price_egp"])
    op.create_index("ix_listings_delivery_date", "listings", ["delivery_date"])
    op.create_index("ix_listings_developer", "listings", ["developer"])

    op.create_table(
        "payment_plans",
        sa.Column("plan_id", sa.Text, primary_key=True),
        sa.Column("listing_id", sa.Text,
                  sa.ForeignKey("listings.listing_id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("down_payment_egp", EGP, nullable=True),
        sa.Column("down_payment_pct", PCT, nullable=True),
        sa.Column("down_payment_source", sa.Text, nullable=True),
        sa.Column("years", sa.Integer, nullable=False),
        sa.Column("frequency", sa.Text, nullable=False),
        sa.Column("delivery_payment_pct", PCT, nullable=True),
        sa.Column("delivery_month", sa.Integer, nullable=True),
        sa.Column("maintenance_pct", PCT, nullable=True),
        sa.CheckConstraint("down_payment_egp >= 0", name="ck_plans_down_payment_egp"),
        sa.CheckConstraint("down_payment_pct BETWEEN 0 AND 100",
                           name="ck_plans_down_payment_pct"),
        sa.CheckConstraint("down_payment_source IN ('egp', 'pct')",
                           name="ck_plans_down_payment_source"),
        # Same rules as PaymentPlan._check_down_payment.
        sa.CheckConstraint(
            "(down_payment_source IS DISTINCT FROM 'egp' OR down_payment_egp IS NOT NULL)"
            " AND (down_payment_source IS DISTINCT FROM 'pct' OR down_payment_pct IS NOT NULL)"
            " AND (down_payment_source IS NOT NULL"
            "      OR (down_payment_egp IS NULL AND down_payment_pct IS NULL))",
            name="ck_plans_down_payment_source_matches",
        ),
        sa.CheckConstraint("years >= 0", name="ck_plans_years"),
        sa.CheckConstraint(FREQUENCY_CHECK, name="ck_plans_frequency"),
        sa.CheckConstraint("delivery_payment_pct BETWEEN 0 AND 100",
                           name="ck_plans_delivery_payment_pct"),
        sa.CheckConstraint("down_payment_pct + delivery_payment_pct <= 100",
                           name="ck_plans_down_plus_delivery"),
        sa.CheckConstraint("delivery_month >= 0", name="ck_plans_delivery_month"),
        sa.CheckConstraint("maintenance_pct >= 0", name="ck_plans_maintenance_pct"),
    )
    op.create_index("ix_payment_plans_listing_id", "payment_plans", ["listing_id"])


def downgrade() -> None:
    op.drop_index("ix_payment_plans_listing_id", table_name="payment_plans")
    op.drop_table("payment_plans")
    for name in ("developer", "delivery_date", "price_egp", "area"):
        op.drop_index(f"ix_listings_{name}", table_name="listings")
    op.drop_table("listings")
    op.drop_table("developers")
