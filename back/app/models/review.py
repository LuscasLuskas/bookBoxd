import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    """A user's public/private opinion on a book: rating + optional text."""

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Soft-delete: the row stays so the placeholder still appears in lists and
    # the unique (user_id, book_id) constraint lets the author re-review later.
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Set only when the service updates an existing review (not on insert),
    # so the frontend can render an "edited" tag without timestamp drift.
    last_edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )
    book: Mapped["Book"] = relationship(  # type: ignore[name-defined]
        "Book", foreign_keys=[book_id]
    )
    likes: Mapped[list["ReviewLike"]] = relationship(  # type: ignore[name-defined]
        "ReviewLike", back_populates="review", cascade="all, delete-orphan"
    )
