import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MembershipStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    LEFT = "LEFT"
    REJECTED = "REJECTED"
    BANNED = "BANNED"
    KICKED = "KICKED"


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "club_id", name="uq_membership_user_club"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    club_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("book_clubs.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus), nullable=False, default=MembershipStatus.PENDING
    )
    kicked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="memberships", foreign_keys=[user_id]
    )
    club: Mapped["BookClub"] = relationship(  # type: ignore[name-defined]
        "BookClub", back_populates="memberships", foreign_keys=[club_id]
    )
