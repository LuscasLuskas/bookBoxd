from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.book_repository import BookRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_book_repository import UserBookRepository
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.club_repo = BookClubRepository(db)
        self.membership_repo = MembershipRepository(db)
        self.book_repo = BookRepository(db)
        self.user_book_repo = UserBookRepository(db)

    def get_profile(self, user: User) -> User:
        return user

    def delete_account(self, user: User, actor: User) -> None:
        if actor.role != Role.MASTER and actor.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para deletar este usuário",
            )
        self._delete_user_transactional(user)

    def _delete_user_transactional(self, user: User) -> None:
        clubs_owned = self.club_repo.get_clubs_owned_by(user.id)
        for club in clubs_owned:
            oldest_member = self.club_repo.get_oldest_active_member(
                club.id, exclude_user_id=user.id
            )
            if oldest_member:
                club.owner_id = oldest_member.user_id
            else:
                self.db.delete(club)

        self.db.flush()

        self.membership_repo.delete_by_user(user.id)
        self.user_book_repo.delete_by_user(user.id)
        self.book_repo.nullify_created_by(user.id, user.name)

        self.db.delete(user)
        self.db.flush()
