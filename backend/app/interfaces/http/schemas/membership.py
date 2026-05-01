from datetime import datetime
from pydantic import BaseModel


class MembershipResponse(BaseModel):
    id: str
    user_id: str
    club_id: str
    status: str
    kicked_until: datetime | None = None
    created_at: datetime


class MembershipActionResponse(BaseModel):
    success: bool
    message: str
