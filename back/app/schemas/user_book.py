from datetime import datetime

from pydantic import BaseModel

from app.models.user_book import UserBookStatus


class UserBookAdd(BaseModel):
    book_id: str
    status: UserBookStatus = UserBookStatus.ADDED


class UserBookUpdate(BaseModel):
    status: UserBookStatus


class UserBookResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    status: UserBookStatus
    # Caller's own rating for this book, drawn from their review. Null = unreviewed.
    rating: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserBookListResponse(BaseModel):
    items: list[UserBookResponse]
    total: int
    limit: int
    offset: int


class UserBookStatsResponse(BaseModel):
    """Reading stats: how many library books the user has in each status."""

    wishlist: int = 0
    added: int = 0
    reading: int = 0
    completed: int = 0
    dropped: int = 0
    total: int = 0
