from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class AccessLogEntity:
    id: UUID
    user_id: Optional[UUID]
    ip_address: Optional[str]
    endpoint: Optional[str]
    created_at: datetime
