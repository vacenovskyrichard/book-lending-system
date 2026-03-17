"""add active loan unique index

Revision ID: 20260316_0002
Revises: 20260316_0001
Create Date: 2026-03-16 23:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260316_0002"
down_revision = "20260316_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_loans_active_book_copy",
        "loans",
        ["book_copy_id"],
        unique=True,
        postgresql_where=sa.text("returned_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_loans_active_book_copy", table_name="loans")
