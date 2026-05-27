from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.reading_goal import (
    DailyLogHistoryResponse,
    DailyLogResponse,
    DailyLogUpsert,
    PublicStreakResponse,
    ReadingGoalResponse,
    ReadingGoalUpsert,
    ReadingStreakResponse,
)
from app.services.reading_goal_service import ReadingGoalService

router = APIRouter(prefix="/me/reading-goal", tags=["reading-goal"])
public_router = APIRouter(prefix="/users", tags=["reading-goal"])


@router.get("", response_model=ReadingGoalResponse | None)
def get_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the user's daily reading goal, or null if none is set."""
    return ReadingGoalService(db).get_goal(current_user)


@router.put("", response_model=ReadingGoalResponse)
def upsert_goal(
    body: ReadingGoalUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates or updates the user's daily reading goal."""
    service = ReadingGoalService(db)
    result = service.upsert_goal(
        body.pages_per_day, current_user, streak_public=body.streak_public
    )
    db.commit()
    return result


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes the user's daily reading goal (history is preserved)."""
    service = ReadingGoalService(db)
    service.delete_goal(current_user)
    db.commit()


@router.post("/log", response_model=DailyLogResponse, status_code=201)
def log_day(
    body: DailyLogUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logs (or updates) reading for a calendar day (defaults to today)."""
    service = ReadingGoalService(db)
    result = service.log_day(body.pages_read, current_user, day=body.date)
    db.commit()
    return result


@router.get("/log/today", response_model=DailyLogResponse | None)
def get_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns today's log entry, or null if not yet logged."""
    return ReadingGoalService(db).get_today_log(current_user)


@router.get("/stats", response_model=ReadingStreakResponse)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Current streak, longest streak, total days met, and today's progress."""
    return ReadingGoalService(db).stats(current_user)


@router.get("/history", response_model=DailyLogHistoryResponse)
def get_history(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Last N days of log entries (most recent first)."""
    return ReadingGoalService(db).history(days, current_user)


@public_router.get(
    "/{user_id}/reading-streak", response_model=PublicStreakResponse
)
def get_public_streak(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Public streak summary for a user — only available if they opted in."""
    return ReadingGoalService(db).public_streak(user_id)
