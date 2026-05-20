import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class Role(str, enum.Enum):
    USER = "USER"
    MASTER = "MASTER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    oauth_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.USER)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    favorite_book_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    favorite_book: Mapped["Book | None"] = relationship(  # type: ignore[name-defined]
        "Book", foreign_keys=[favorite_book_id]
    )
    books_created: Mapped[list["Book"]] = relationship(  # type: ignore[name-defined]
        "Book", back_populates="creator", foreign_keys="Book.created_by"
    )
    memberships: Mapped[list["Membership"]] = relationship(  # type: ignore[name-defined]
        "Membership", back_populates="user", foreign_keys="Membership.user_id"
    )
    clubs_owned: Mapped[list["BookClub"]] = relationship(  # type: ignore[name-defined]
        "BookClub", back_populates="owner", foreign_keys="BookClub.owner_id"
    )
    user_books: Mapped[list["UserBook"]] = relationship(  # type: ignore[name-defined]
        "UserBook", back_populates="user"
    )
