import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book_club import BookClub
from app.models.membership import Membership, MembershipStatus
from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.membership_repository import MembershipRepository
from app.schemas.book_club import BookClubCreate, BookClubUpdate


class BookClubService:
    def __init__(self, db: Session):
        self.db = db
        self.club_repo = BookClubRepository(db)
        self.membership_repo = MembershipRepository(db)

    def create(self, data: BookClubCreate, current_user: User) -> BookClub:
        club = BookClub(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            owner_id=current_user.id,
        )
        self.club_repo.create(club)

        owner_membership = Membership(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            club_id=club.id,
            status=MembershipStatus.ACTIVE,
        )
        self.membership_repo.create(owner_membership)
        return club

    def get_by_id(self, club_id: str) -> BookClub:
        club = self.club_repo.get_by_id(club_id)
        if not club:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado")
        return club
    
    def list_all(self) -> list[BookClub]:
        return self.club_repo.get_all()

    def update(self, club_id: str, data: BookClubUpdate, current_user: User) -> BookClub:
        club = self.get_by_id(club_id)
        self._assert_owner_or_master(club, current_user)
        if data.name is not None:
            club.name = data.name
        if data.description is not None:
            club.description = data.description
        return self.club_repo.save(club)

    def delete(self, club_id: str, current_user: User) -> None:
        club = self.get_by_id(club_id)
        self._assert_owner_or_master(club, current_user)
        self.club_repo.delete(club)
        self.db.flush()

    def _assert_owner_or_master(self, club: BookClub, user: User) -> None:
        if club.owner_id != user.id and user.role != Role.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o dono ou MASTER pode modificar este clube",
            )
