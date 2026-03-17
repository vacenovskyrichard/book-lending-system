from fastapi import HTTPException, status

from app.models.db.book import Book
from app.models.db.book_copy import BookCopyStatus
from app.models.schemas.book import BookCreate, BookRead
from app.repositories.book_repository import BookRepository


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    def create_book(self, payload: BookCreate) -> BookRead:
        book = self.repository.create(
            title=payload.title,
            author=payload.author,
            copies_count=payload.copies_count,
        )
        if book is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Book creation failed.")
        return self._to_schema(book)

    def get_book(self, book_id: int) -> BookRead:
        book = self.repository.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
        return self._to_schema(book)

    def list_books(self, *, available_only: bool = False) -> list[BookRead]:
        books = self.repository.list_all(available_only=available_only)
        return [self._to_schema(book) for book in books]

    def _to_schema(self, book: Book) -> BookRead:
        total_copies = len(book.copies)
        available_copies = sum(1 for copy in book.copies if copy.status == BookCopyStatus.AVAILABLE)
        return BookRead(
            id=book.id,
            title=book.title,
            author=book.author,
            total_copies=total_copies,
            available_copies=available_copies,
            is_available=available_copies > 0,
            created_at=book.created_at,
        )
