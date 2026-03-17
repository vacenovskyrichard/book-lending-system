from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_book_service
from app.models.schemas.book import BookCreate, BookRead
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    payload: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    return service.create_book(payload)


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
