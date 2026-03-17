from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.user_repository import UserRepository
from app.services.book_service import BookService
from app.services.loan_service import LoanService
from app.services.user_service import UserService


def get_user_repository(session: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_book_repository(session: Session = Depends(get_db_session)) -> BookRepository:
    return BookRepository(session)


def get_loan_repository(session: Session = Depends(get_db_session)) -> LoanRepository:
    return LoanRepository(session)


def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)


def get_book_service(repository: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repository)


def get_loan_service(session: Session = Depends(get_db_session)) -> LoanService:
    return LoanService(
        loan_repository=LoanRepository(session),
        user_repository=UserRepository(session),
        book_repository=BookRepository(session),
        session=session,
    )
