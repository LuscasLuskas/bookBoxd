from app.infrastructure.db.models.club_book import ClubBook
from app.infrastructure.db.repositories.book_club_repository import BookClubRepository
from app.infrastructure.db.repositories.book_repository import BookRepository
from app.infrastructure.db.repositories.club_book_repository import ClubBookRepository
from sqlalchemy.ext.asyncio import AsyncSession


class ClubBookService:
    def __init__(self) -> None:
        self.club_repo = BookClubRepository()
        self.book_repo = BookRepository()
        self.club_book_repo = ClubBookRepository()

    async def add_book_to_club(self, session: AsyncSession, club_id, book_id, added_by) -> ClubBook:
        club = await self.club_repo.get_by_id(session, club_id)
        if club is None:
            raise ValueError("Club not found")
        book = await self.book_repo.get_by_id(session, book_id)
        if book is None:
            raise ValueError("Book not found")

        existing = await self.club_book_repo.get_by_club_and_book(session, club_id, book_id)
        if existing:
            return existing

        club_book = ClubBook(club_id=club_id, book_id=book_id, added_by=added_by)
        return await self.club_book_repo.create(session, club_book)
