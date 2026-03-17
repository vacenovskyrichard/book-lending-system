from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str
    author: str
    copies_count: int = Field(default=1, ge=1, le=100)


class BookRead(BaseModel):
    id: int
    title: str
    author: str
    total_copies: int
    available_copies: int
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
