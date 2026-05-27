import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReadingGoal(Base):
    """A user's personal daily reading goal (pages/day).

    One goal per user; updating overwrites in place. Daily progress lives in
    DailyReadingLog so history survives goal changes.
    """

    __tablename__ = "reading_goals"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_reading_goal_user"),
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
    pages_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    # When True, the user's streak summary is visible on their public profile.
    streak_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DailyReadingLog(Base):
    """One row per (user, calendar day). pages_read is cumulative for the day.

    goal_target is a snapshot of the user's goal at log-time so historical
    "goal met" status is preserved even if the user later changes the goal.
    """

    __tablename__ = "daily_reading_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_log_user_date"),
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
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pages_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goal_target: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
