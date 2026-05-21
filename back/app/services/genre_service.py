import uuid

from sqlalchemy.orm import Session

from app.models.genre import Genre
from app.repositories.genre_repository import GenreRepository


class GenreService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GenreRepository(db)

    def list_genres(self) -> list[Genre]:
        return self.repo.list_all()

    def get_or_create(self, name: str) -> Genre:
        name = name.strip()[:100]
        existing = self.repo.get_by_name(name)
        if existing:
            return existing
        return self.repo.create(Genre(id=str(uuid.uuid4()), name=name))

    def assign_to_book(self, book_id: str, names: list[str]) -> None:
        """Links a book to the given genres, creating any that don't exist yet."""
        for raw in names:
            name = raw.strip()
            if not name:
                continue
            genre = self.get_or_create(name)
            if not self.repo.get_link(book_id, genre.id):
                self.repo.link(book_id, genre.id)
