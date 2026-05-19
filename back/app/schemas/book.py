from datetime import datetime

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=255)
    synopsis: str | None = None


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    synopsis: str | None
    created_by: str | None
    created_by_name_snapshot: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    limit: int
    offset: int
