from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.genre import BookGenre, Genre


class GenreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Genre | None:
        return (
            self.db.query(Genre)
            .filter(func.lower(Genre.name) == name.lower())
            .first()
        )

    def create(self, genre: Genre) -> Genre:
        self.db.add(genre)
        self.db.flush()
        self.db.refresh(genre)
        return genre

    def list_all(self) -> list[Genre]:
        return self.db.query(Genre).order_by(Genre.name).all()

    def get_link(self, book_id: str, genre_id: str) -> BookGenre | None:
        return (
            self.db.query(BookGenre)
            .filter(BookGenre.book_id == book_id, BookGenre.genre_id == genre_id)
            .first()
        )

    def link(self, book_id: str, genre_id: str) -> None:
        self.db.add(BookGenre(book_id=book_id, genre_id=genre_id))
        self.db.flush()

    def genres_for_books(self, book_ids: list[str]) -> dict[str, list[Genre]]:
        """Maps each book id to its genres in a single query (no N+1)."""
        if not book_ids:
            return {}
        rows = (
            self.db.query(BookGenre.book_id, Genre)
            .join(Genre, Genre.id == BookGenre.genre_id)
            .filter(BookGenre.book_id.in_(book_ids))
            .all()
        )
        result: dict[str, list[Genre]] = {}
        for book_id, genre in rows:
            result.setdefault(book_id, []).append(genre)
        return result
