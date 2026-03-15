"""create domain tables

Revision ID: 20260315_0002
Revises: 20260315_0001
Create Date: 2026-03-15 00:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260315_0002"
down_revision = "20260315_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("document_number", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_customers_email"),
        sa.UniqueConstraint("document_number", name="uq_customers_document_number"),
    )
    op.create_index("ix_customers_id", "customers", ["id"], unique=False)
    op.create_index("ix_customers_email", "customers", ["email"], unique=False)

    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("document_number", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_suppliers_email"),
        sa.UniqueConstraint("document_number", name="uq_suppliers_document_number"),
    )
    op.create_index("ix_suppliers_id", "suppliers", ["id"], unique=False)
    op.create_index("ix_suppliers_email", "suppliers", ["email"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_products_id", "products", ["id"], unique=False)

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_services_id", "services", ["id"], unique=False)

    ticket_status = postgresql.ENUM(
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED",
        name="ticketstatus",
        create_type=False,
    )
    work_order_status = postgresql.ENUM(
        "CREATED",
        "STARTED",
        "FINISHED",
        "CANCELLED",
        name="workorderstatus",
        create_type=False,
    )
    transaction_type = postgresql.ENUM(
        "DEPOSIT",
        "WITHDRAW",
        "PAYMENT",
        "REFUND",
        name="transactiontype",
        create_type=False,
    )
    payable_status = postgresql.ENUM(
        "PENDING",
        "PAID",
        "CANCELLED",
        name="accountspayablestatus",
        create_type=False,
    )
    receivable_status = postgresql.ENUM(
        "PENDING",
        "RECEIVED",
        "CANCELLED",
        name="accountsreceivablestatus",
        create_type=False,
    )

    ticket_status.create(op.get_bind(), checkfirst=True)
    work_order_status.create(op.get_bind(), checkfirst=True)
    transaction_type.create(op.get_bind(), checkfirst=True)
    payable_status.create(op.get_bind(), checkfirst=True)
    receivable_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", ticket_status, nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(), nullable=False, server_default="MEDIUM"),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_tickets_id", "tickets", ["id"], unique=False)

    op.create_table(
        "work_orders",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("assigned_user_id", sa.Integer(), nullable=False),
        sa.Column("status", work_order_status, nullable=False, server_default="CREATED"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.ForeignKeyConstraint(["assigned_user_id"], ["users.id"]),
    )
    op.create_index("ix_work_orders_id", "work_orders", ["id"], unique=False)

    op.create_table(
        "wallets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id", name="uq_wallets_user_id"),
    )
    op.create_index("ix_wallets_id", "wallets", ["id"], unique=False)

    op.create_table(
        "financial_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("wallet_id", sa.Integer(), nullable=False),
        sa.Column("type", transaction_type, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
    )
    op.create_index("ix_financial_transactions_id", "financial_transactions", ["id"], unique=False)

    op.create_table(
        "accounts_payable",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", payable_status, nullable=False, server_default="PENDING"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
    )
    op.create_index("ix_accounts_payable_id", "accounts_payable", ["id"], unique=False)

    op.create_table(
        "accounts_receivable",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", receivable_status, nullable=False, server_default="PENDING"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_accounts_receivable_id", "accounts_receivable", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_accounts_receivable_id", table_name="accounts_receivable")
    op.drop_table("accounts_receivable")

    op.drop_index("ix_accounts_payable_id", table_name="accounts_payable")
    op.drop_table("accounts_payable")

    op.drop_index("ix_financial_transactions_id", table_name="financial_transactions")
    op.drop_table("financial_transactions")

    op.drop_index("ix_wallets_id", table_name="wallets")
    op.drop_table("wallets")

    op.drop_index("ix_work_orders_id", table_name="work_orders")
    op.drop_table("work_orders")

    op.drop_index("ix_tickets_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_index("ix_services_id", table_name="services")
    op.drop_table("services")

    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_suppliers_email", table_name="suppliers")
    op.drop_index("ix_suppliers_id", table_name="suppliers")
    op.drop_table("suppliers")

    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_index("ix_customers_id", table_name="customers")
    op.drop_table("customers")

    sa.Enum(name="accountsreceivablestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="accountspayablestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="transactiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="workorderstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="ticketstatus").drop(op.get_bind(), checkfirst=True)
