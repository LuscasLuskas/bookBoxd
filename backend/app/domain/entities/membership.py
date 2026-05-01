from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class MembershipEntity:
    id: UUID
    user_id: UUID
    club_id: UUID
    status: str
    kicked_until: Optional[datetime]
    created_at: datetime
