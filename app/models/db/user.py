from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    loans: Mapped[list["Loan"]] = relationship(
        back_populates="borrower",
        foreign_keys="Loan.borrower_user_id",
    )
    processed_returns: Mapped[list["Loan"]] = relationship(
        back_populates="returned_by",
        foreign_keys="Loan.returned_by_user_id",
    )
