"""Add extended fields to task table.

Revision ID: 002
Revises: 001
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add priority, tags, due_date, recurrence, parent_id, and soft delete fields."""

    # Add new columns to task table
    op.add_column("task", sa.Column("priority", sa.String(10), nullable=False, server_default="MEDIUM"))
    op.add_column("task", sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True))
    op.add_column("task", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("task", sa.Column("recurrence", sa.String(10), nullable=False, server_default="NONE"))
    op.add_column("task", sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("task", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("task", sa.Column("deletion_reason", sa.String(500), nullable=True))

    # Add foreign key constraint for parent_id (self-referencing)
    op.create_foreign_key(
        "fk_task_parent_id",
        "task",
        "task",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL"
    )

    # Add check constraints
    op.create_check_constraint(
        "ck_task_priority",
        "task",
        "priority IN ('HIGH', 'MEDIUM', 'LOW')"
    )
    op.create_check_constraint(
        "ck_task_recurrence",
        "task",
        "recurrence IN ('NONE', 'DAILY', 'WEEKLY', 'MONTHLY')"
    )

    # Create indexes for new fields
    op.create_index("ix_task_priority", "task", ["priority"], unique=False)
    op.create_index("ix_task_due_date", "task", ["due_date"], unique=False, postgresql_where=sa.text("due_date IS NOT NULL"))
    op.create_index("ix_task_deleted_at", "task", ["deleted_at"], unique=False, postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_task_recurrence", "task", ["recurrence"], unique=False, postgresql_where=sa.text("recurrence != 'NONE'"))
    op.create_index("ix_task_tags", "task", ["tags"], unique=False, postgresql_using="gin")
    op.create_index("ix_task_parent_id", "task", ["parent_id"], unique=False)


def downgrade() -> None:
    """Remove extended fields from task table."""

    # Drop indexes
    op.drop_index("ix_task_parent_id", table_name="task")
    op.drop_index("ix_task_tags", table_name="task")
    op.drop_index("ix_task_recurrence", table_name="task")
    op.drop_index("ix_task_deleted_at", table_name="task")
    op.drop_index("ix_task_due_date", table_name="task")
    op.drop_index("ix_task_priority", table_name="task")

    # Drop check constraints
    op.drop_constraint("ck_task_recurrence", "task", type_="check")
    op.drop_constraint("ck_task_priority", "task", type_="check")

    # Drop foreign key
    op.drop_constraint("fk_task_parent_id", "task", type_="foreignkey")

    # Drop columns
    op.drop_column("task", "deletion_reason")
    op.drop_column("task", "deleted_at")
    op.drop_column("task", "parent_id")
    op.drop_column("task", "recurrence")
    op.drop_column("task", "due_date")
    op.drop_column("task", "tags")
    op.drop_column("task", "priority")
