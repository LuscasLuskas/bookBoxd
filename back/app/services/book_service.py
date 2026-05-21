import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.user import User
from app.repositories.book_repository import BookRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.user_book_repository import UserBookRepository
from app.schemas.book import BookCreate, BookDetailResponse, BookResponse
from app.schemas.tag import TagResponse
from app.services.genre_service import GenreService
from app.services.open_library_service import OpenLibraryService


class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BookRepository(db)

    def create(self, data: BookCreate, current_user: User) -> Book:
        # Imports from Open Library are idempotent: if a book with the same
        # external_id already exists, reuse it instead of duplicating the catalog.
        if data.external_id:
            existing = self.repo.get_by_external_id(data.external_id)
            if existing:
                return existing

        synopsis = data.synopsis
        subjects: list[str] = []
        if data.external_id:
            meta = OpenLibraryService().fetch_work_meta(data.external_id)
            if not synopsis:
                synopsis = meta["description"]
            subjects = meta["subjects"]

        book = Book(
            id=str(uuid.uuid4()),
            title=data.title[:500],
            author=data.author[:255],
            synopsis=synopsis,
            cover_url=data.cover_url,
            external_id=data.external_id,
            published_year=data.published_year,
            isbn=data.isbn,
            created_by=current_user.id,
            created_by_name_snapshot=current_user.name,
        )
        created = self.repo.create(book)

        # Auto-assign genres imported from Open Library subjects.
        if subjects:
            GenreService(self.db).assign_to_book(created.id, subjects)

        return created

    def get_by_id(self, book_id: str) -> Book:
        book = self.repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
        return book

    def list_books(
        self,
        limit: int = 20,
        offset: int = 0,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
    ) -> tuple[list[BookResponse], int]:
        items, total = self.repo.list(
            limit=limit, offset=offset, title=title, author=author, genre=genre
        )
        return self.enrich_books(items), total

    def get_book_detail(self, book_id: str) -> BookDetailResponse:
        book = self.get_by_id(book_id)
        avg, count = self._rating_stats([book.id]).get(book.id, (None, 0))
        genres = GenreRepository(self.db).genres_for_books([book.id]).get(book.id, [])
        tag_rows = TagRepository(self.db).tags_for_book(book.id)

        detail = BookDetailResponse.model_validate(book)
        detail.avg_rating = round(avg, 2) if avg is not None else None
        detail.ratings_count = count
        detail.genres = sorted(g.name for g in genres)
        detail.tags = [
            TagResponse(id=tag.id, name=tag.name, added_by=link.added_by)
            for tag, link in tag_rows
        ]
        return detail

    def enrich_books(self, books: list[Book]) -> list[BookResponse]:
        """Attaches aggregated rating and genre data to a list of books."""
        book_ids = [b.id for b in books]
        rating_stats = self._rating_stats(book_ids)
        genres_map = GenreRepository(self.db).genres_for_books(book_ids)

        responses: list[BookResponse] = []
        for book in books:
            resp = BookResponse.model_validate(book)
            avg, count = rating_stats.get(book.id, (None, 0))
            resp.avg_rating = round(avg, 2) if avg is not None else None
            resp.ratings_count = count
            resp.genres = sorted(g.name for g in genres_map.get(book.id, []))
            responses.append(resp)
        return responses

    def _rating_stats(self, book_ids: list[str]) -> dict[str, tuple[float, int]]:
        return UserBookRepository(self.db).rating_stats_for_books(book_ids)
