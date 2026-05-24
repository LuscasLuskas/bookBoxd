import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ForumThread(Base):
    """A discussion thread inside a club's forum. May be tied to a book."""

    __tablename__ = "forum_threads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    club_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("book_clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # True when the thread was auto-opened by the monthly-book hook; lets the
    # service unpin it when that monthly book is cleared.
    auto_created: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    book: Mapped["Book | None"] = relationship(  # type: ignore[name-defined]
        "Book", foreign_keys=[book_id]
    )
    creator: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[created_by]
    )
    posts: Mapped[list["ForumPost"]] = relationship(  # type: ignore[name-defined]
        "ForumPost", back_populates="thread", cascade="all, delete-orphan"
    )
