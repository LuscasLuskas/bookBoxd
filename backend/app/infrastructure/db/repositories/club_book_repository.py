from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.club_book import ClubBook


class ClubBookRepository:
    async def get_by_club_and_book(self, session: AsyncSession, club_id, book_id) -> Optional[ClubBook]:
        result = await session.execute(
            select(ClubBook).where(ClubBook.club_id == club_id, ClubBook.book_id == book_id)
        )
        return result.scalars().first()

    async def create(self, session: AsyncSession, club_book: ClubBook) -> ClubBook:
        session.add(club_book)
        await session.flush()
        return club_book
