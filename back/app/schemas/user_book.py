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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserBookListResponse(BaseModel):
    items: list[UserBookResponse]
    total: int
    limit: int
    offset: int
