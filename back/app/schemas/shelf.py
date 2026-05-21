from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.book import BookResponse


class ShelfCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ShelfBookAdd(BaseModel):
    book_id: str


class ShelfResponse(BaseModel):
    id: str
    user_id: str
    name: str
    book_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ShelfListResponse(BaseModel):
    items: list[ShelfResponse]


class ShelfDetailResponse(ShelfResponse):
    books: list[BookResponse] = []
