from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class UserEntity:
    id: UUID
    email: str
    name: Optional[str]
    oauth_provider: Optional[str]
    oauth_id: Optional[str]
    role: str
    created_at: datetime
