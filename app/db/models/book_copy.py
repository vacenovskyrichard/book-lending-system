from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookCopyStatus(str, Enum):
    AVAILABLE = "available"
    LOANED = "loaned"


class BookCopy(Base):
    __tablename__ = "book_copies"
    __table_args__ = (
        UniqueConstraint("book_id", "inventory_number", name="uq_book_copy_inventory_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    inventory_number: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[BookCopyStatus] = mapped_column(
        SqlEnum(BookCopyStatus, name="book_copy_status"),
        default=BookCopyStatus.AVAILABLE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    book: Mapped["Book"] = relationship(back_populates="copies")
    loans: Mapped[list["Loan"]] = relationship(back_populates="book_copy")
