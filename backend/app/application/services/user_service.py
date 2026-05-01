from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.repositories.book_repository import BookRepository
from app.infrastructure.db.repositories.book_club_repository import BookClubRepository
from app.infrastructure.db.repositories.membership_repository import MembershipRepository
from app.infrastructure.db.repositories.user_book_repository import UserBookRepository


class UserService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.book_repo = BookRepository()
        self.club_repo = BookClubRepository()
        self.membership_repo = MembershipRepository()
        self.user_book_repo = UserBookRepository()

    async def delete_user(self, session: AsyncSession, user_id) -> None:
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise ValueError("User not found")

        owned_clubs = await self.club_repo.list_owned_by(session, user_id)
        for club in owned_clubs:
            replacements = await self.membership_repo.list_active_members_by_club(session, club.id, exclude_user_id=user_id)
            if not replacements:
                raise ValueError("Cannot delete user while they own a club with no active replacement")
            club.owner_id = replacements[0].user_id
            await self.club_repo.create(session, club)

        books = await self.book_repo.list_by_created_by(session, user_id)
        for book in books:
            book.created_by = None
            await self.book_repo.update(session, book)

        await self.membership_repo.delete_by_user(session, user_id)
        await self.user_book_repo.delete_by_user(session, user_id)
        await self.user_repo.delete(session, user)
