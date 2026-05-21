import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tag(Base):
    """A community tag. Shared across all users — anyone can apply it to a book."""

    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", name="uq_tag_name"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class BookTag(Base):
    """Join row linking a book to a community tag, tracking who applied it."""

    __tablename__ = "book_tags"

    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    added_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
