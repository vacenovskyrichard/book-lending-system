from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index(
            "uq_loans_active_book_copy",
            "book_copy_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
            sqlite_where=text("returned_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("book_copies.id", ondelete="RESTRICT"), nullable=False, index=True)
    borrower_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)

    book_copy: Mapped["BookCopy"] = relationship(back_populates="loans")
    borrower: Mapped["User"] = relationship(back_populates="loans", foreign_keys=[borrower_user_id])
    returned_by: Mapped["User | None"] = relationship(
        back_populates="processed_returns",
        foreign_keys=[returned_by_user_id],
    )
