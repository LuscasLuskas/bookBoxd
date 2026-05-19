import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClubBook(Base):
    __tablename__ = "club_books"
    __table_args__ = (
        UniqueConstraint("club_id", "book_id", name="uq_club_book"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    club_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("book_clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    added_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    club: Mapped["BookClub"] = relationship(  # type: ignore[name-defined]
        "BookClub", back_populates="club_books"
    )
    book: Mapped["Book"] = relationship(  # type: ignore[name-defined]
        "Book", back_populates="club_books"
    )
    adder: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[added_by]
    )
