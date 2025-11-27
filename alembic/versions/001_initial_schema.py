"""Initial schema - create members, entry_logs, and payment_logs tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create members table
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create entry_logs table
    op.create_table(
        "entry_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entry_logs_member_id"), "entry_logs", ["member_id"])

    # Create payment_logs table
    op.create_table(
        "payment_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_logs_member_id"), "payment_logs", ["member_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_logs_member_id"), table_name="payment_logs")
    op.drop_table("payment_logs")
    op.drop_index(op.f("ix_entry_logs_member_id"), table_name="entry_logs")
    op.drop_table("entry_logs")
    op.drop_table("members")
