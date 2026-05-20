from sqlalchemy.orm import Session

from app.models.reading_register import ReadingRegister


class ReadingRegisterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_book_and_user(
        self, monthly_book_id: str, user_id: str
    ) -> ReadingRegister | None:
        return (
            self.db.query(ReadingRegister)
            .filter(
                ReadingRegister.monthly_book_id == monthly_book_id,
                ReadingRegister.user_id == user_id,
            )
            .first()
        )

    def list_by_monthly_book(self, monthly_book_id: str) -> list[ReadingRegister]:
        return (
            self.db.query(ReadingRegister)
            .filter(ReadingRegister.monthly_book_id == monthly_book_id)
            .order_by(ReadingRegister.created_at.asc())
            .all()
        )

    def create(self, register: ReadingRegister) -> ReadingRegister:
        self.db.add(register)
        self.db.flush()
        self.db.refresh(register)
        return register

    def add_all(self, registers: list[ReadingRegister]) -> None:
        self.db.add_all(registers)
        self.db.flush()

    def save(self, register: ReadingRegister) -> ReadingRegister:
        self.db.flush()
        self.db.refresh(register)
        return register
