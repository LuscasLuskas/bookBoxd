from sqlalchemy.orm import Session

from app.models.book_club import BookClub
from app.models.membership import Membership, MembershipStatus


class BookClubRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[BookClub]:
        return self.db.query(BookClub).all()

    def get_by_id(self, club_id: str) -> BookClub | None:
        return self.db.query(BookClub).filter(BookClub.id == club_id).first()

    def create(self, club: BookClub) -> BookClub:
        self.db.add(club)
        self.db.flush()
        self.db.refresh(club)
        return club

    def save(self, club: BookClub) -> BookClub:
        self.db.flush()
        self.db.refresh(club)
        return club

    def delete(self, club: BookClub) -> None:
        self.db.delete(club)

    def get_clubs_owned_by(self, user_id: str) -> list[BookClub]:
        return self.db.query(BookClub).filter(BookClub.owner_id == user_id).all()

    def get_oldest_active_member(self, club_id: str, exclude_user_id: str) -> Membership | None:
        return (
            self.db.query(Membership)
            .filter(
                Membership.club_id == club_id,
                Membership.status == MembershipStatus.ACTIVE,
                Membership.user_id != exclude_user_id,
            )
            .order_by(Membership.created_at.asc())
            .first()
        )
