import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookClub(Base):
    __tablename__ = "book_clubs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    owner: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="clubs_owned", foreign_keys=[owner_id]
    )
    memberships: Mapped[list["Membership"]] = relationship(  # type: ignore[name-defined]
        "Membership", back_populates="club", cascade="all, delete-orphan"
    )
    club_books: Mapped[list["ClubBook"]] = relationship(  # type: ignore[name-defined]
        "ClubBook", back_populates="club", cascade="all, delete-orphan"
    )
