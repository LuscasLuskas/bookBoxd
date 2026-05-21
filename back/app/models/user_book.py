import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserBookStatus(str, enum.Enum):
    WISHLIST = "WISHLIST"
    ADDED = "ADDED"
    READING = "READING"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"


class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[UserBookStatus] = mapped_column(
        Enum(UserBookStatus), nullable=False, default=UserBookStatus.ADDED
    )
    # Personal star rating (0.5–5.0, half-star steps). Null = unrated.
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="user_books"
    )
    book: Mapped["Book"] = relationship(  # type: ignore[name-defined]
        "Book", back_populates="user_books"
    )
