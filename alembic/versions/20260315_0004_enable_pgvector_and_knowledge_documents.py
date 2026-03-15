"""enable pgvector and create knowledge documents

Revision ID: 20260315_0004
Revises: 20260315_0003
Create Date: 2026-03-15 02:10:00
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "20260315_0004"
down_revision = "20260315_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_knowledge_documents_id", "knowledge_documents", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_knowledge_documents_id", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
