from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class ClubBookEntity:
    id: UUID
    club_id: UUID
    book_id: UUID
    added_by: Optional[UUID]
    created_at: datetime
