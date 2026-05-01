from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.book_club import BookClub


class BookClubRepository:
    async def get_by_id(self, session: AsyncSession, club_id) -> Optional[BookClub]:
        result = await session.execute(select(BookClub).where(BookClub.id == club_id))
        return result.scalars().first()

    async def create(self, session: AsyncSession, club: BookClub) -> BookClub:
        session.add(club)
        await session.flush()
        return club

    async def delete(self, session: AsyncSession, club: BookClub) -> None:
        await session.delete(club)

    async def list_owned_by(self, session: AsyncSession, owner_id):
        result = await session.execute(select(BookClub).where(BookClub.owner_id == owner_id))
        return result.scalars().all()
