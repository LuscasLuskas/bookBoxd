from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class BookClubEntity:
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    created_at: datetime
