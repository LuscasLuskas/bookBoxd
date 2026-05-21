import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Genre(Base):
    """A book-level genre. Populated automatically from Open Library subjects."""

    __tablename__ = "genres"
    __table_args__ = (UniqueConstraint("name", name="uq_genre_name"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class BookGenre(Base):
    """Join row linking a book to a genre."""

    __tablename__ = "book_genres"

    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
