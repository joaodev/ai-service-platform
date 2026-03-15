"""create ai agent logs table

Revision ID: 20260315_0005
Revises: 20260315_0004
Create Date: 2026-03-15 03:40:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260315_0005"
down_revision = "20260315_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_agent_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("input_message", sa.Text(), nullable=False),
        sa.Column("actions_taken", sa.JSON(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_agent_logs_id", "ai_agent_logs", ["id"], unique=False)
    op.create_index("ix_ai_agent_logs_user_id", "ai_agent_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_agent_logs_user_id", table_name="ai_agent_logs")
    op.drop_index("ix_ai_agent_logs_id", table_name="ai_agent_logs")
    op.drop_table("ai_agent_logs")
