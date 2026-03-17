from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models.book_copy import BookCopy
from app.db.models.loan import Loan


class LoanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, book_copy_id: int, borrower_user_id: int) -> Loan:
        loan = Loan(book_copy_id=book_copy_id, borrower_user_id=borrower_user_id)
        self.session.add(loan)
        self.session.flush()
        return loan

    def get_by_id(self, loan_id: int) -> Loan | None:
        statement = (
            select(Loan)
            .options(joinedload(Loan.book_copy).joinedload(BookCopy.book))
            .where(Loan.id == loan_id)
        )
        return self.session.scalar(statement)

    def list_all(self, *, active_only: bool = False) -> list[Loan]:
        statement = (
            select(Loan)
            .options(joinedload(Loan.book_copy).joinedload(BookCopy.book))
            .order_by(Loan.id.desc())
        )
        if active_only:
            statement = statement.where(Loan.returned_at.is_(None))
        return list(self.session.scalars(statement).unique().all())

    def mark_returned(self, loan: Loan, *, returned_by_user_id: int) -> Loan:
        loan.returned_at = datetime.now(timezone.utc)
        loan.returned_by_user_id = returned_by_user_id
        self.session.add(loan)
        self.session.flush()
        return loan

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
