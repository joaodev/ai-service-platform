"""create ai agent actions table

Revision ID: 20260315_0007
Revises: 20260315_0006
Create Date: 2026-03-15 05:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260315_0007"
down_revision = "20260315_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_agent_actions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_agent_actions_id", "ai_agent_actions", ["id"], unique=False)
    op.create_index("ix_ai_agent_actions_agent_name", "ai_agent_actions", ["agent_name"], unique=False)
    op.create_index("ix_ai_agent_actions_event_type", "ai_agent_actions", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_agent_actions_event_type", table_name="ai_agent_actions")
    op.drop_index("ix_ai_agent_actions_agent_name", table_name="ai_agent_actions")
    op.drop_index("ix_ai_agent_actions_id", table_name="ai_agent_actions")
    op.drop_table("ai_agent_actions")
