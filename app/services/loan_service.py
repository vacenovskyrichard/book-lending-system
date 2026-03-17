from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.loan import LoanCreate, LoanRead, LoanReturn
from app.db.models.book_copy import BookCopyStatus
from app.db.models.loan import Loan
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.user_repository import UserRepository


class LoanService:
    def __init__(
        self,
        loan_repository: LoanRepository,
        user_repository: UserRepository,
        book_repository: BookRepository,
        session: Session,
    ) -> None:
        self.loan_repository = loan_repository
        self.user_repository = user_repository
        self.book_repository = book_repository
        self.session = session

    def borrow_book(self, payload: LoanCreate, *, actor_user_id: int) -> LoanRead:
        user = self.user_repository.get_by_id(actor_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing user not found.")

        book = self.book_repository.get_by_id(payload.book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

        available_copy = self.book_repository.get_first_available_copy(payload.book_id)
        if not available_copy:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No available copy for this book.",
            )

        try:
            self.book_repository.update_copy_status(available_copy, status=BookCopyStatus.LOANED)
            loan = self.loan_repository.create(
                book_copy_id=available_copy.id,
                borrower_user_id=actor_user_id,
            )
            self.loan_repository.commit()
            self.session.refresh(loan)
        except IntegrityError as exc:
            self.loan_repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No available copy for this book.",
            ) from exc
        except SQLAlchemyError as exc:
            self.loan_repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create loan.",
            ) from exc

        created_loan = self.loan_repository.get_by_id(loan.id)
        if created_loan is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Loan creation failed.")
        return self._to_schema(created_loan)

    def return_book(self, payload: LoanReturn, *, actor_user_id: int) -> LoanRead:
        user = self.user_repository.get_by_id(actor_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Returning user not found.")

        loan = self.loan_repository.get_by_id(payload.loan_id)
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found.")
        if loan.returned_at is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Loan is already closed.")
        if loan.borrower_user_id != actor_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the borrowing user can return this book.",
            )

        try:
            self.book_repository.update_copy_status(loan.book_copy, status=BookCopyStatus.AVAILABLE)
            self.loan_repository.mark_returned(loan, returned_by_user_id=actor_user_id)
            self.loan_repository.commit()
            self.session.refresh(loan)
        except SQLAlchemyError as exc:
            self.loan_repository.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to return loan.",
            ) from exc

        returned_loan = self.loan_repository.get_by_id(loan.id)
        if returned_loan is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Loan return failed.")
        return self._to_schema(returned_loan)

    def list_loans(self) -> list[LoanRead]:
        return [self._to_schema(loan) for loan in self.loan_repository.list_all()]

    def _to_schema(self, loan: Loan) -> LoanRead:
        return LoanRead(
            id=loan.id,
            book_id=loan.book_copy.book_id,
            book_copy_id=loan.book_copy_id,
            book_title=loan.book_copy.book.title,
            borrower_user_id=loan.borrower_user_id,
            borrowed_at=loan.borrowed_at,
            returned_at=loan.returned_at,
            returned_by_user_id=loan.returned_by_user_id,
            is_active=loan.returned_at is None,
        )
