from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class UserBookEntity:
    id: UUID
    user_id: UUID
    book_id: UUID
    status: Optional[str]
    created_at: datetime
    updated_at: datetime
