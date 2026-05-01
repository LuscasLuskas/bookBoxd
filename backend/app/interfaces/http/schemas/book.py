from datetime import datetime
from pydantic import BaseModel


class BookCreateRequest(BaseModel):
    title: str
    author: str | None = None
    synopsis: str | None = None


class BookResponse(BaseModel):
    id: str
    title: str
    author: str | None = None
    synopsis: str | None = None
    created_by: str | None = None
    created_by_name_snapshot: str | None = None
    created_at: datetime
