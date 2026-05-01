from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.book_club import BookClub
from app.infrastructure.db.models.membership import Membership
from app.infrastructure.db.models.club_book import ClubBook
from app.infrastructure.db.repositories.book_club_repository import BookClubRepository
from app.infrastructure.db.repositories.membership_repository import MembershipRepository
from app.infrastructure.db.repositories.club_book_repository import ClubBookRepository


class ClubService:
    def __init__(self) -> None:
        self.club_repo = BookClubRepository()
        self.membership_repo = MembershipRepository()
        self.club_book_repo = ClubBookRepository()

    async def create_club(self, session: AsyncSession, owner, name: str, description: str | None) -> BookClub:
        club = BookClub(name=name, description=description, owner_id=owner.id)
        return await self.club_repo.create(session, club)

    async def transfer_ownership(self, session: AsyncSession, club_id, new_owner_id) -> BookClub:
        club = await self.club_repo.get_by_id(session, club_id)
        if club is None:
            raise ValueError("Club not found")
        club.owner_id = new_owner_id
        return await self.club_repo.create(session, club)

    async def delete_club(self, session: AsyncSession, club_id) -> None:
        club = await self.club_repo.get_by_id(session, club_id)
        if club is None:
            raise ValueError("Club not found")

        await session.execute(delete(Membership).where(Membership.club_id == club_id))
        await session.execute(delete(ClubBook).where(ClubBook.club_id == club_id))
        await self.club_repo.delete(session, club)
