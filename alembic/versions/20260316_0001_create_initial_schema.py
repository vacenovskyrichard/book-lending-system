"""create initial schema

Revision ID: 20260316_0001
Revises:
Create Date: 2026-03-16 17:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260316_0001"
down_revision = None
branch_labels = None
depends_on = None

book_copy_status = sa.Enum("available", "loaned", name="book_copy_status")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_books_author"), "books", ["author"], unique=False)
    op.create_index(op.f("ix_books_id"), "books", ["id"], unique=False)
    op.create_index(op.f("ix_books_title"), "books", ["title"], unique=False)

    op.create_table(
        "book_copies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("inventory_number", sa.Integer(), nullable=False),
        sa.Column("status", book_copy_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("book_id", "inventory_number", name="uq_book_copy_inventory_number"),
    )
    op.create_index(op.f("ix_book_copies_book_id"), "book_copies", ["book_id"], unique=False)
    op.create_index(op.f("ix_book_copies_id"), "book_copies", ["id"], unique=False)

    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_copy_id", sa.Integer(), nullable=False),
        sa.Column("borrower_user_id", sa.Integer(), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["book_copy_id"], ["book_copies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["borrower_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["returned_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_loans_book_copy_id"), "loans", ["book_copy_id"], unique=False)
    op.create_index(op.f("ix_loans_borrower_user_id"), "loans", ["borrower_user_id"], unique=False)
    op.create_index(op.f("ix_loans_id"), "loans", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_loans_id"), table_name="loans")
    op.drop_index(op.f("ix_loans_borrower_user_id"), table_name="loans")
    op.drop_index(op.f("ix_loans_book_copy_id"), table_name="loans")
    op.drop_table("loans")

    op.drop_index(op.f("ix_book_copies_id"), table_name="book_copies")
    op.drop_index(op.f("ix_book_copies_book_id"), table_name="book_copies")
    op.drop_table("book_copies")

    op.drop_index(op.f("ix_books_title"), table_name="books")
    op.drop_index(op.f("ix_books_id"), table_name="books")
    op.drop_index(op.f("ix_books_author"), table_name="books")
    op.drop_table("books")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
