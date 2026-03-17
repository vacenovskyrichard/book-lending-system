"""add unique constraint for books

Revision ID: 20260317_0003
Revises: 20260316_0002
Create Date: 2026-03-17 11:30:00
"""

from alembic import op


revision = "20260317_0003"
down_revision = "20260316_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_books_title_author", "books", ["title", "author"])


def downgrade() -> None:
    op.drop_constraint("uq_books_title_author", "books", type_="unique")
