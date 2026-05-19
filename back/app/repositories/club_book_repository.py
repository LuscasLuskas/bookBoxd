from sqlalchemy.orm import Session

from app.models.club_book import ClubBook


class ClubBookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_club_and_book(self, club_id: str, book_id: str) -> ClubBook | None:
        return (
            self.db.query(ClubBook)
            .filter(ClubBook.club_id == club_id, ClubBook.book_id == book_id)
            .first()
        )

    def get_by_id(self, club_book_id: str) -> ClubBook | None:
        return self.db.query(ClubBook).filter(ClubBook.id == club_book_id).first()

    def list_by_club(
        self, club_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[ClubBook], int]:
        query = self.db.query(ClubBook).filter(ClubBook.club_id == club_id)
        total = query.count()
        items = query.order_by(ClubBook.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, club_book: ClubBook) -> ClubBook:
        self.db.add(club_book)
        self.db.flush()
        self.db.refresh(club_book)
        return club_book

    def delete(self, club_book: ClubBook) -> None:
        self.db.delete(club_book)
