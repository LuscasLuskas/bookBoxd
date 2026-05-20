import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.user import User
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate
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
        if not synopsis and data.external_id:
            synopsis = OpenLibraryService().fetch_description(data.external_id)

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
        return self.repo.create(book)

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
    ) -> tuple[list[Book], int]:
        return self.repo.list(limit=limit, offset=offset, title=title, author=author)
