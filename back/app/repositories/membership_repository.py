from sqlalchemy.orm import Session, aliased

from app.models.membership import Membership, MembershipStatus


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, membership_id: str) -> Membership | None:
        return self.db.query(Membership).filter(Membership.id == membership_id).first()

    def get_by_user_and_club(self, user_id: str, club_id: str) -> Membership | None:
        return (
            self.db.query(Membership)
            .filter(Membership.user_id == user_id, Membership.club_id == club_id)
            .first()
        )

    def get_member(self, club_id: str, user_id: str) -> Membership | None:
        return (
            self.db.query(Membership)
            .filter(
                Membership.club_id == club_id,
                Membership.user_id == user_id,
            )
            .first()
        )

    def list_by_club(
        self, club_id: str, status: MembershipStatus | None = None
    ) -> list[Membership]:
        query = self.db.query(Membership).filter(Membership.club_id == club_id)
        if status:
            query = query.filter(Membership.status == status)
        return query.all()

    def create(self, membership: Membership) -> Membership:
        self.db.add(membership)
        self.db.flush()
        self.db.refresh(membership)
        return membership

    def save(self, membership: Membership) -> Membership:
        self.db.flush()
        self.db.refresh(membership)
        return membership

    def delete_by_user(self, user_id: str) -> None:
        self.db.query(Membership).filter(Membership.user_id == user_id).delete()

    def shares_active_club(self, user_a_id: str, user_b_id: str) -> bool:
        """True iff both users have an ACTIVE membership in some common club."""
        a = aliased(Membership)
        b = aliased(Membership)
        row = (
            self.db.query(a.club_id)
            .join(b, a.club_id == b.club_id)
            .filter(
                a.user_id == user_a_id,
                a.status == MembershipStatus.ACTIVE,
                b.user_id == user_b_id,
                b.status == MembershipStatus.ACTIVE,
            )
            .first()
        )
        return row is not None
