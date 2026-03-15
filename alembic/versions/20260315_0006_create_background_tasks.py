"""create background tasks table

Revision ID: 20260315_0006
Revises: 20260315_0005
Create Date: 2026-03-15 04:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260315_0006"
down_revision = "20260315_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "background_tasks",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_background_tasks_id", "background_tasks", ["id"], unique=False)
    op.create_index("ix_background_tasks_task_type", "background_tasks", ["task_type"], unique=False)
    op.create_index("ix_background_tasks_status", "background_tasks", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_background_tasks_status", table_name="background_tasks")
    op.drop_index("ix_background_tasks_task_type", table_name="background_tasks")
    op.drop_index("ix_background_tasks_id", table_name="background_tasks")
    op.drop_table("background_tasks")
