from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.book import Book
from app.db.models.book_copy import BookCopy, BookCopyStatus


class BookRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, title: str, author: str, copies_count: int) -> Book | None:
        book = Book(title=title, author=author)
        self.session.add(book)
        self.session.flush()

        copies = [
            BookCopy(book_id=book.id, inventory_number=index + 1, status=BookCopyStatus.AVAILABLE)
            for index in range(copies_count)
        ]
        self.session.add_all(copies)
        self.session.commit()
        self.session.refresh(book)
        return self.get_by_id(book.id)

    def get_by_id(self, book_id: int) -> Book | None:
        statement = select(Book).options(selectinload(Book.copies)).where(Book.id == book_id)
        return self.session.scalar(statement)

    def list_all(self, *, available_only: bool = False) -> list[Book]:
        statement: Select[tuple[Book]] = select(Book).options(selectinload(Book.copies)).order_by(Book.id)
        if available_only:
            statement = statement.where(Book.copies.any(BookCopy.status == BookCopyStatus.AVAILABLE))
        return list(self.session.scalars(statement).unique().all())

    def get_first_available_copy(self, book_id: int) -> BookCopy | None:
        statement = (
            select(BookCopy)
            .where(
                BookCopy.book_id == book_id,
                BookCopy.status == BookCopyStatus.AVAILABLE,
            )
            .order_by(BookCopy.inventory_number)
            .with_for_update(skip_locked=True)
        )
        return self.session.scalar(statement)

    def update_copy_status(self, book_copy: BookCopy, *, status: BookCopyStatus) -> BookCopy:
        book_copy.status = status
        self.session.add(book_copy)
        self.session.flush()
        return book_copy
