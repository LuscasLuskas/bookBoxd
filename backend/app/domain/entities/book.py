from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class BookEntity:
    id: UUID
    title: str
    author: Optional[str]
    synopsis: Optional[str]
    created_by: Optional[UUID]
    created_by_name_snapshot: Optional[str]
    created_at: datetime
