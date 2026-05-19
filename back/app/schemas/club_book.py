from datetime import datetime

from pydantic import BaseModel


class ClubBookAdd(BaseModel):
    book_id: str


class ClubBookResponse(BaseModel):
    id: str
    club_id: str
    book_id: str
    added_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClubBookListResponse(BaseModel):
    items: list[ClubBookResponse]
    total: int
    limit: int
    offset: int
