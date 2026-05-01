import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.db.models.base import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
