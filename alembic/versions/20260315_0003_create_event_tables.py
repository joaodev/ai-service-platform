"""create event tables

Revision ID: 20260315_0003
Revises: 20260315_0002
Create Date: 2026-03-15 01:20:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260315_0003"
down_revision = "20260315_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_event_logs_id", "event_logs", ["id"], unique=False)
    op.create_index("ix_event_logs_event_type", "event_logs", ["event_type"], unique=False)

    op.create_table(
        "webhook_configs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_webhook_configs_id", "webhook_configs", ["id"], unique=False)
    op.create_index("ix_webhook_configs_event_type", "webhook_configs", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_webhook_configs_event_type", table_name="webhook_configs")
    op.drop_index("ix_webhook_configs_id", table_name="webhook_configs")
    op.drop_table("webhook_configs")

    op.drop_index("ix_event_logs_event_type", table_name="event_logs")
    op.drop_index("ix_event_logs_id", table_name="event_logs")
    op.drop_table("event_logs")
