import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    thread_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Soft-delete: keep the row so readers see "[excluded comment]" where it was.
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Set only on edit, not on insert — drives the "(edited)" tag.
    last_edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    thread: Mapped["ForumThread"] = relationship(  # type: ignore[name-defined]
        "ForumThread", back_populates="posts"
    )
    user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )
