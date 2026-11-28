"""S2-M3-02 make 5 listing fields nullable (unknown = NULL)

Revision ID: 0006
Revises: 0001
Create Date: 2026-11-28
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0001"   # sprint rule: new migrations start from 0001
branch_labels = None
depends_on = None

COLUMNS = {
    "developer": sa.Text,
    "area_sqm": sa.Numeric(10, 2),
    "down_payment_pct": sa.Numeric(6, 3),
    "years": sa.Integer,
    "frequency": sa.Text,
}


def upgrade() -> None:
    for name, column_type in COLUMNS.items():
        op.alter_column("listings", name, existing_type=column_type(), nullable=True)


def downgrade() -> None:
    # Fails if a row already has NULL here. Delete or fill those rows first.
    for name, column_type in COLUMNS.items():
        op.alter_column("listings", name, existing_type=column_type(), nullable=False)