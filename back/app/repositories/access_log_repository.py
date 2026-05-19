from sqlalchemy.orm import Session

from app.models.access_log import AccessLog


class AccessLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AccessLog) -> None:
        self.db.add(log)
        self.db.flush()
