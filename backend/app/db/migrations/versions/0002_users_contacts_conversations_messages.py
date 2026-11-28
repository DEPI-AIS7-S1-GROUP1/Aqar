"""Create users, user_contacts, conversations and messages

Tables for user management and conversational chat system.

Rules:
* user_contacts is separate to prevent phone numbers from leaking into AI prompts.
* No foreign keys to tables owned by other team members.
* CHECK constraints enforce enum-like values at the database level.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-26
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

ROLE_CHECK = "role IN ('customer', 'broker')"
MESSAGE_ROLE_CHECK = "role IN ('user', 'ai', 'broker', 'system')"
CONVERSATION_MODE_VALUES = ('search', 'compare', 'negotiate', 'followup')
CONVERSATION_MODE_CHECK = f"mode IN {CONVERSATION_MODE_VALUES}"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Text, primary_key=True),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.CheckConstraint(ROLE_CHECK, name="ck_users_role"),
    )

    op.create_table(
        "user_contacts",
        sa.Column("user_id", sa.Text,
                  sa.ForeignKey("users.user_id", ondelete="CASCADE"),
                  primary_key=True),
        sa.Column("phone", sa.Text, nullable=True),
        sa.Column("contact_consent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "conversations",
        sa.Column("conversation_id", sa.Text, primary_key=True),
        sa.Column("user_id", sa.Text,
                  sa.ForeignKey("users.user_id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("mode", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.CheckConstraint(CONVERSATION_MODE_CHECK, name="ck_conversations_mode"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    op.create_table(
        "messages",
        sa.Column("message_id", sa.Text, primary_key=True),
        sa.Column("conversation_id", sa.Text,
                  sa.ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("card_listing_ids", sa.ARRAY(sa.Text), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.CheckConstraint(MESSAGE_ROLE_CHECK, name="ck_messages_role"),
    )
    op.create_index("ix_messages_conversation_created", "messages",
                    ["conversation_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_messages_conversation_created", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_user_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_table("user_contacts")
    op.drop_table("users")
