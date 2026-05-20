from sqlalchemy.orm import Session

from app.models.club_monthly_book import ClubMonthlyBook


class ClubMonthlyBookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, monthly_book_id: str) -> ClubMonthlyBook | None:
        return (
            self.db.query(ClubMonthlyBook)
            .filter(ClubMonthlyBook.id == monthly_book_id)
            .first()
        )

    def get_active_by_club_and_book(
        self, club_id: str, book_id: str
    ) -> ClubMonthlyBook | None:
        return (
            self.db.query(ClubMonthlyBook)
            .filter(
                ClubMonthlyBook.club_id == club_id,
                ClubMonthlyBook.book_id == book_id,
                ClubMonthlyBook.is_active.is_(True),
            )
            .first()
        )

    def list_by_club(
        self, club_id: str, active_only: bool = False
    ) -> list[ClubMonthlyBook]:
        query = self.db.query(ClubMonthlyBook).filter(
            ClubMonthlyBook.club_id == club_id
        )
        if active_only:
            query = query.filter(ClubMonthlyBook.is_active.is_(True))
        return query.order_by(ClubMonthlyBook.start_date.desc()).all()

    def create(self, monthly_book: ClubMonthlyBook) -> ClubMonthlyBook:
        self.db.add(monthly_book)
        self.db.flush()
        self.db.refresh(monthly_book)
        return monthly_book

    def save(self, monthly_book: ClubMonthlyBook) -> ClubMonthlyBook:
        self.db.flush()
        self.db.refresh(monthly_book)
        return monthly_book
