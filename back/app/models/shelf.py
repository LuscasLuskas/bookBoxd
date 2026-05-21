import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Shelf(Base):
    """A user-owned custom collection of books (e.g. "Favorites", "Summer 2026")."""

    __tablename__ = "shelves"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_shelf_user_name"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ShelfBook(Base):
    """Join row placing a book on a shelf."""

    __tablename__ = "shelf_books"

    shelf_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shelves.id", ondelete="CASCADE"), primary_key=True
    )
    book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
