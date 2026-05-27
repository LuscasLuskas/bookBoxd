from datetime import date as _date, datetime

from pydantic import BaseModel


# ---- Goal ----


class ReadingGoalUpsert(BaseModel):
    """Body for creating or updating the daily goal.

    streak_public is optional: omitted keeps existing setting (or defaults to
    False on first create).
    """

    pages_per_day: int
    streak_public: bool | None = None


class ReadingGoalResponse(BaseModel):
    id: str
    user_id: str
    pages_per_day: int
    streak_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicStreakResponse(BaseModel):
    """Streak summary exposed publicly when the user opted in."""

    user_id: str
    pages_per_day: int
    current_streak: int
    longest_streak: int
    total_days_met: int


# ---- Daily log ----


class DailyLogUpsert(BaseModel):
    """Body for logging today's (or a specific day's) reading."""

    pages_read: int
    # Optional: defaults to today (UTC) if omitted.
    date: _date | None = None


class DailyLogResponse(BaseModel):
    id: str
    user_id: str
    date: _date
    pages_read: int
    goal_target: int
    goal_met: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---- Stats / history ----


class ReadingStreakResponse(BaseModel):
    """Aggregated streak stats for the user."""

    current_streak: int
    longest_streak: int
    total_days_met: int
    today_logged: bool
    today_goal_met: bool
    today_pages_read: int
    today_goal_target: int | None


class DailyLogHistoryResponse(BaseModel):
    items: list[DailyLogResponse]
