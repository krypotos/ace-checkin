"""Change payment amount from INTEGER (cents) to DECIMAL (dollars)

Revision ID: 002
Revises: 001
Create Date: 2026-01-21

This migration:
1. Changes payment_logs.amount from INTEGER (cents) to NUMERIC(10,2) (dollars)
2. Converts existing data from cents to dollars
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add a temporary column with the new type
    op.add_column(
        "payment_logs",
        sa.Column("amount_new", sa.Numeric(10, 2), nullable=True),
    )

    # Step 2: Convert existing data from cents to dollars
    op.execute("UPDATE payment_logs SET amount_new = amount / 100.0")

    # Step 3: Drop the old column
    op.drop_column("payment_logs", "amount")

    # Step 4: Rename the new column to 'amount'
    op.alter_column("payment_logs", "amount_new", new_column_name="amount")

    # Step 5: Set NOT NULL constraint
    op.alter_column("payment_logs", "amount", nullable=False)


def downgrade() -> None:
    # Step 1: Add a temporary column with the old type
    op.add_column(
        "payment_logs",
        sa.Column("amount_old", sa.Integer(), nullable=True),
    )

    # Step 2: Convert data back from dollars to cents
    op.execute("UPDATE payment_logs SET amount_old = CAST(amount * 100 AS INTEGER)")

    # Step 3: Drop the decimal column
    op.drop_column("payment_logs", "amount")

    # Step 4: Rename the old column back to 'amount'
    op.alter_column("payment_logs", "amount_old", new_column_name="amount")

    # Step 5: Set NOT NULL constraint
    op.alter_column("payment_logs", "amount", nullable=False)
