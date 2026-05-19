from datetime import datetime

from pydantic import BaseModel, Field


class BookClubCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class BookClubUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class BookClubResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
