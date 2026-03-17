from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.book import BookCopyCreate, BookCreate, BookRead
from app.dependencies import get_book_service
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    payload: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return service.create_book(payload)


@router.post("/{book_id}/copies", response_model=BookRead)
def add_book_copies(
    book_id: int,
    payload: BookCopyCreate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return service.add_copies(book_id, payload)


@router.get("", response_model=list[BookRead])
def list_books(
    available_only: bool = Query(default=False),
    service: BookService = Depends(get_book_service),
) -> list[BookRead]:
    return service.list_books(available_only=available_only)


@router.get("/{book_id}", response_model=BookRead)
def get_book(
    book_id: int,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return service.get_book(book_id)
