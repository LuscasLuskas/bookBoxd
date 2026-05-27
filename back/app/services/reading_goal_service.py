import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.reading_goal import DailyReadingLog, ReadingGoal
from app.models.user import User
from app.repositories.reading_goal_repository import ReadingGoalRepository
from app.schemas.reading_goal import (
    DailyLogHistoryResponse,
    DailyLogResponse,
    PublicStreakResponse,
    ReadingGoalResponse,
    ReadingStreakResponse,
)


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _log_to_response(log: DailyReadingLog) -> DailyLogResponse:
    return DailyLogResponse(
        id=log.id,
        user_id=log.user_id,
        date=log.date,
        pages_read=log.pages_read,
        goal_target=log.goal_target,
        goal_met=log.pages_read >= log.goal_target,
        updated_at=log.updated_at,
    )


class ReadingGoalService:
    """Personal daily reading goal + streak.

    Validation lives here (not in Pydantic field_validator) per project convention:
    field_validator ValueErrors crash with 500 instead of returning 400.
    """

    MIN_PAGES = 1
    MAX_PAGES = 10_000

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReadingGoalRepository(db)

    # ---- Goal CRUD ----

    def get_goal(self, current_user: User) -> ReadingGoalResponse | None:
        goal = self.repo.get_by_user(current_user.id)
        return ReadingGoalResponse.model_validate(goal) if goal else None

    def upsert_goal(
        self,
        pages_per_day: int,
        current_user: User,
        streak_public: bool | None = None,
    ) -> ReadingGoalResponse:
        if pages_per_day < self.MIN_PAGES or pages_per_day > self.MAX_PAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A meta deve estar entre {self.MIN_PAGES} e {self.MAX_PAGES} páginas",
            )
        goal = self.repo.get_by_user(current_user.id)
        if goal:
            goal.pages_per_day = pages_per_day
            if streak_public is not None:
                goal.streak_public = streak_public
            self.db.flush()
            self.db.refresh(goal)
        else:
            goal = self.repo.create(
                ReadingGoal(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    pages_per_day=pages_per_day,
                    streak_public=bool(streak_public) if streak_public is not None else False,
                )
            )
        return ReadingGoalResponse.model_validate(goal)

    def public_streak(self, user_id: str) -> PublicStreakResponse:
        """Returns the streak summary for any user whose goal is public.

        Raises 404 if the user has no goal or has not made it public — same
        status either way so visibility status itself isn't leaked.
        """
        goal = self.repo.get_by_user(user_id)
        if not goal or not goal.streak_public:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Streak não disponível",
            )
        all_logs = self.repo.list_logs_for_user(user_id)
        by_date: dict[date, DailyReadingLog] = {l.date: l for l in all_logs}
        today = _today()
        return PublicStreakResponse(
            user_id=user_id,
            pages_per_day=goal.pages_per_day,
            current_streak=self._current_streak(by_date, today),
            longest_streak=self._longest_streak(all_logs),
            total_days_met=sum(
                1 for l in all_logs if l.pages_read >= l.goal_target
            ),
        )

    def delete_goal(self, current_user: User) -> None:
        goal = self.repo.get_by_user(current_user.id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma meta de leitura definida",
            )
        self.repo.delete(goal)

    # ---- Daily log ----

    def log_day(
        self,
        pages_read: int,
        current_user: User,
        day: date | None = None,
    ) -> DailyLogResponse:
        if pages_read < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O número de páginas não pode ser negativo",
            )
        if pages_read > 100_000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de páginas implausível",
            )
        goal = self.repo.get_by_user(current_user.id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Defina uma meta diária antes de registrar leitura",
            )
        log_day = day or _today()
        if log_day > _today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível registrar leitura em data futura",
            )
        existing = self.repo.get_log(current_user.id, log_day)
        if existing:
            existing.pages_read = pages_read
            # Refresh goal target snapshot to the current goal at edit time.
            existing.goal_target = goal.pages_per_day
            self.db.flush()
            self.db.refresh(existing)
            return _log_to_response(existing)
        created = self.repo.create_log(
            DailyReadingLog(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                date=log_day,
                pages_read=pages_read,
                goal_target=goal.pages_per_day,
            )
        )
        return _log_to_response(created)

    def get_today_log(self, current_user: User) -> DailyLogResponse | None:
        log = self.repo.get_log(current_user.id, _today())
        return _log_to_response(log) if log else None

    def history(self, days: int, current_user: User) -> DailyLogHistoryResponse:
        days = max(1, min(days, 365))
        logs = self.repo.list_recent_logs(current_user.id, days)
        return DailyLogHistoryResponse(items=[_log_to_response(l) for l in logs])

    # ---- Streak ----

    def stats(self, current_user: User) -> ReadingStreakResponse:
        goal = self.repo.get_by_user(current_user.id)
        all_logs = self.repo.list_logs_for_user(current_user.id)
        # Map date -> log for fast lookup.
        by_date: dict[date, DailyReadingLog] = {l.date: l for l in all_logs}
        today = _today()

        current_streak = self._current_streak(by_date, today)
        longest_streak = self._longest_streak(all_logs)
        total_met = sum(1 for l in all_logs if l.pages_read >= l.goal_target)

        today_log = by_date.get(today)
        return ReadingStreakResponse(
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_days_met=total_met,
            today_logged=today_log is not None,
            today_goal_met=bool(today_log and today_log.pages_read >= today_log.goal_target),
            today_pages_read=today_log.pages_read if today_log else 0,
            today_goal_target=goal.pages_per_day if goal else None,
        )

    @staticmethod
    def _current_streak(by_date: dict[date, DailyReadingLog], today: date) -> int:
        """Walk back from today counting consecutive met days.

        Today gets a grace pass: if today isn't logged yet, the streak isn't
        broken — it just stops accruing until logged. Yesterday onward is strict.
        """
        streak = 0
        cursor = today
        today_log = by_date.get(today)
        if today_log:
            if today_log.pages_read >= today_log.goal_target:
                streak += 1
                cursor = today - timedelta(days=1)
            else:
                # Logged today but didn't meet → streak is currently 0.
                return 0
        else:
            # No log today yet — start checking from yesterday.
            cursor = today - timedelta(days=1)
        while True:
            log = by_date.get(cursor)
            if log and log.pages_read >= log.goal_target:
                streak += 1
                cursor -= timedelta(days=1)
            else:
                break
        return streak

    @staticmethod
    def _longest_streak(logs: list[DailyReadingLog]) -> int:
        """Longest consecutive run of met days across all history."""
        met_dates = sorted(
            {l.date for l in logs if l.pages_read >= l.goal_target}
        )
        if not met_dates:
            return 0
        longest = 1
        run = 1
        for prev, cur in zip(met_dates, met_dates[1:]):
            if (cur - prev).days == 1:
                run += 1
                longest = max(longest, run)
            else:
                run = 1
        return longest
