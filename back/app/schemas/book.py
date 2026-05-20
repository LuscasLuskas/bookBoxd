from datetime import datetime

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=255)
    synopsis: str | None = None
    cover_url: str | None = Field(None, max_length=500)
    external_id: str | None = Field(None, max_length=100)
    published_year: int | None = None
    isbn: str | None = Field(None, max_length=20)


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    synopsis: str | None
    cover_url: str | None
    external_id: str | None
    published_year: int | None
    isbn: str | None
    created_by: str | None
    created_by_name_snapshot: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    limit: int
    offset: int


class ExternalBookResult(BaseModel):
    """A book returned by the Open Library search, not yet in the catalog."""

    external_id: str
    title: str
    author: str
    cover_url: str | None = None
    published_year: int | None = None
    isbn: str | None = None


class ExternalSearchResponse(BaseModel):
    items: list[ExternalBookResult]
