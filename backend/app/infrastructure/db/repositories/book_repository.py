from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.book import Book


class BookRepository:
    async def get_by_id(self, session: AsyncSession, book_id) -> Optional[Book]:
        result = await session.execute(select(Book).where(Book.id == book_id))
        return result.scalars().first()

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(Book))
        return result.scalars().all()

    async def list_by_created_by(self, session: AsyncSession, user_id):
        result = await session.execute(select(Book).where(Book.created_by == user_id))
        return result.scalars().all()

    async def create(self, session: AsyncSession, book: Book) -> Book:
        session.add(book)
        await session.flush()
        return book

    async def update(self, session: AsyncSession, book: Book) -> Book:
        session.add(book)
        await session.flush()
        return book
