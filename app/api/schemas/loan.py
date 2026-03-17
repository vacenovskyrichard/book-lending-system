from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    book_id: int


class LoanReturn(BaseModel):
    loan_id: int


class LoanRead(BaseModel):
    id: int
    book_id: int
    book_copy_id: int
    book_title: str
    borrower_user_id: int
    borrowed_at: datetime
    returned_at: datetime | None
    returned_by_user_id: int | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
