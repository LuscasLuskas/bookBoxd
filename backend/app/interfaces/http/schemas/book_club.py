from datetime import datetime
from pydantic import BaseModel


class ClubCreateRequest(BaseModel):
    name: str
    description: str | None = None


class ClubResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str
    created_at: datetime
