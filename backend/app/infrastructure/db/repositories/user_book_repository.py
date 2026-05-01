from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.infrastructure.db.models.user_book import UserBook


class UserBookRepository:
    async def delete_by_user(self, session: AsyncSession, user_id) -> None:
        await session.execute(delete(UserBook).where(UserBook.user_id == user_id))

    async def get_by_user_and_book(self, session: AsyncSession, user_id, book_id) -> Optional[UserBook]:
        result = await session.execute(
            select(UserBook).where(UserBook.user_id == user_id, UserBook.book_id == book_id)
        )
        return result.scalars().first()

    async def create(self, session: AsyncSession, user_book: UserBook) -> UserBook:
        session.add(user_book)
        await session.flush()
        return user_book
