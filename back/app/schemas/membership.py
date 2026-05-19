from datetime import datetime

from pydantic import BaseModel

from app.models.membership import MembershipStatus


class MembershipResponse(BaseModel):
    id: str
    user_id: str
    club_id: str
    status: MembershipStatus
    kicked_until: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KickRequest(BaseModel):
    kicked_until: datetime


class MembershipListResponse(BaseModel):
    items: list[MembershipResponse]
    total: int
