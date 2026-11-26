"""S2-M3-01 listing photos and extra fields

Adds the 5 optional Listing fields from Appendix A (contracts-v2) and a
one-row data_meta table that counts data versions.
Rules:
* New listing columns are nullable with no default. Unknown is NULL, never 0.
* data_meta.data_version is a global counter, bumped by every ingest/import.
  (listings.data_version from 0001 is a different, per-row text column. Untouched.)

Revision ID: 0003
Revises: 0001
Create Date: 2026-11-27
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("title", sa.Text, nullable=True))
    op.add_column("listings", sa.Column("unit_type", sa.Text, nullable=True))
    op.add_column("listings", sa.Column("bedrooms", sa.Integer, nullable=True))
    op.add_column("listings", sa.Column("image_urls", sa.ARRAY(sa.Text), nullable=True))
    op.add_column("listings", sa.Column("image_credit", sa.Text, nullable=True))
    op.create_check_constraint("ck_listings_bedrooms", "listings", "bedrooms >= 0")

    op.create_table(
        "data_meta",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("data_version", sa.Integer, nullable=False),
        sa.CheckConstraint("id = 1", name="ck_data_meta_single_row"),
    )
    op.execute("INSERT INTO data_meta (id, data_version) VALUES (1, 0)")


def downgrade() -> None:
    op.drop_table("data_meta")
    op.drop_constraint("ck_listings_bedrooms", "listings", type_="check")
    for name in ("image_credit", "image_urls", "bedrooms", "unit_type", "title"):
        op.drop_column("listings", name)