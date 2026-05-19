import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.user import User
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate


class BookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BookRepository(db)

    def create(self, data: BookCreate, current_user: User) -> Book:
        book = Book(
            id=str(uuid.uuid4()),
            title=data.title,
            author=data.author,
            synopsis=data.synopsis,
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
