from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.reading_goal import DailyReadingLog, ReadingGoal


class ReadingGoalRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---- Goal ----

    def get_by_user(self, user_id: str) -> ReadingGoal | None:
        return (
            self.db.query(ReadingGoal)
            .filter(ReadingGoal.user_id == user_id)
            .first()
        )

    def create(self, goal: ReadingGoal) -> ReadingGoal:
        self.db.add(goal)
        self.db.flush()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: ReadingGoal) -> None:
        self.db.delete(goal)

    # ---- Daily logs ----

    def get_log(self, user_id: str, day: date) -> DailyReadingLog | None:
        return (
            self.db.query(DailyReadingLog)
            .filter(DailyReadingLog.user_id == user_id, DailyReadingLog.date == day)
            .first()
        )

    def create_log(self, log: DailyReadingLog) -> DailyReadingLog:
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log

    def list_logs_for_user(
        self, user_id: str, since: date | None = None
    ) -> list[DailyReadingLog]:
        q = self.db.query(DailyReadingLog).filter(DailyReadingLog.user_id == user_id)
        if since is not None:
            q = q.filter(DailyReadingLog.date >= since)
        return q.order_by(DailyReadingLog.date.desc()).all()

    def list_recent_logs(
        self, user_id: str, days: int
    ) -> list[DailyReadingLog]:
        """Last N days of logs (ordered most recent first)."""
        if days <= 0:
            return []
        since = date.today() - timedelta(days=days - 1)
        return self.list_logs_for_user(user_id, since=since)
