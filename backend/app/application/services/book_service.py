from app.infrastructure.db.models.book import Book
from app.infrastructure.db.repositories.book_repository import BookRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BookService:
    def __init__(self) -> None:
        self.book_repo = BookRepository()

    async def create_book(self, session: AsyncSession, title: str, author: str | None, synopsis: str | None, user) -> Book:
        book = Book(
            title=title,
            author=author,
            synopsis=synopsis,
            created_by=user.id,
            created_by_name_snapshot=user.name,
        )
        return await self.book_repo.create(session, book)
