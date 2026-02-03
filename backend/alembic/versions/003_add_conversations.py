"""Add conversation and chat_message tables.

Revision ID: 003
Revises: 002
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create conversation and chat_message tables."""

    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Create foreign key constraint
    op.create_foreign_key(
        "fk_conversation_user_id",
        "conversation",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Create chat_message table
    op.create_table(
        "chatmessage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.String(10000), nullable=False, server_default=""),
        sa.Column("tool_name", sa.String(100), nullable=True),
        sa.Column("tool_input", sa.String(5000), nullable=True),
        sa.Column("tool_output", sa.String(5000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Create foreign key constraint
    op.create_foreign_key(
        "fk_chatmessage_conversation_id",
        "chatmessage",
        "conversation",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Add conversations relationship to user table (add cascade delete)
    # This is handled by SQLAlchemy relationships, not as a database constraint


def downgrade() -> None:
    """Drop conversation and chat_message tables."""

    # Drop foreign key constraint first
    op.drop_constraint("fk_chatmessage_conversation_id", "chatmessage", type_="foreignkey")
    op.drop_constraint("fk_conversation_user_id", "conversation", type_="foreignkey")

    # Drop tables
    op.drop_table("chatmessage")
    op.drop_table("conversation")