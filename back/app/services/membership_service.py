import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.membership import Membership, MembershipStatus
from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.membership_repository import MembershipRepository


class MembershipService:
    def __init__(self, db: Session):
        self.db = db
        self.club_repo = BookClubRepository(db)
        self.membership_repo = MembershipRepository(db)

    def join(self, club_id: str, current_user: User) -> Membership:
        club = self._get_club_or_404(club_id)
        existing = self.membership_repo.get_by_user_and_club(current_user.id, club_id)

        if existing:
            if existing.status == MembershipStatus.BANNED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário banido deste clube",
                )
            if existing.status == MembershipStatus.KICKED:
                kicked_until = existing.kicked_until
                if kicked_until and kicked_until.tzinfo is None:
                    kicked_until = kicked_until.replace(tzinfo=timezone.utc)
                if kicked_until and kicked_until > datetime.now(timezone.utc):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Usuário expulso até {existing.kicked_until.isoformat()}",
                    )
                existing.status = MembershipStatus.PENDING
                existing.kicked_until = None
                existing.updated_at = datetime.now(timezone.utc)
                return self.membership_repo.save(existing)
            if existing.status in (MembershipStatus.LEFT, MembershipStatus.REJECTED):
                existing.status = MembershipStatus.PENDING
                existing.updated_at = datetime.now(timezone.utc)
                return self.membership_repo.save(existing)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe uma solicitação ativa com status {existing.status.value}",
            )

        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            club_id=club_id,
            status=MembershipStatus.PENDING,
        )
        return self.membership_repo.create(membership)

    def approve(self, club_id: str, user_id: str, current_user: User) -> Membership:
        self._assert_owner_or_master(club_id, current_user)
        membership = self._get_membership_or_404(club_id, user_id)
        if membership.status != MembershipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas membros PENDING podem ser aprovados",
            )
        membership.status = MembershipStatus.ACTIVE
        membership.updated_at = datetime.now(timezone.utc)
        return self.membership_repo.save(membership)

    def reject(self, club_id: str, user_id: str, current_user: User) -> Membership:
        self._assert_owner_or_master(club_id, current_user)
        membership = self._get_membership_or_404(club_id, user_id)
        if membership.status != MembershipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas membros PENDING podem ser rejeitados",
            )
        membership.status = MembershipStatus.REJECTED
        membership.updated_at = datetime.now(timezone.utc)
        return self.membership_repo.save(membership)

    def leave(self, club_id: str, current_user: User) -> Membership:
        membership = self._get_membership_or_404(club_id, current_user.id)
        club = self._get_club_or_404(club_id)

        if club.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O dono não pode sair do clube. Transfira o ownership antes.",
            )
        if membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas membros ACTIVE podem sair",
            )
        membership.status = MembershipStatus.LEFT
        membership.updated_at = datetime.now(timezone.utc)
        return self.membership_repo.save(membership)

    def ban(self, club_id: str, user_id: str, current_user: User) -> Membership:
        self._assert_owner_or_master(club_id, current_user)
        membership = self._get_membership_or_404(club_id, user_id)
        if membership.status == MembershipStatus.BANNED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário já está banido",
            )
        membership.status = MembershipStatus.BANNED
        membership.updated_at = datetime.now(timezone.utc)
        return self.membership_repo.save(membership)

    def kick(self, club_id: str, user_id: str, kicked_until: datetime, current_user: User) -> Membership:
        self._assert_owner_or_master(club_id, current_user)
        membership = self._get_membership_or_404(club_id, user_id)
        if membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Apenas membros ACTIVE podem ser expulsos",
            )
        if kicked_until <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="kicked_until deve ser uma data futura",
            )
        membership.status = MembershipStatus.KICKED
        membership.kicked_until = kicked_until
        membership.updated_at = datetime.now(timezone.utc)
        return self.membership_repo.save(membership)

    def list_members(self, club_id: str, status_filter: MembershipStatus | None = None) -> list[Membership]:
        self._get_club_or_404(club_id)
        return self.membership_repo.list_by_club(club_id, status=status_filter)

    def _get_club_or_404(self, club_id: str):
        club = self.club_repo.get_by_id(club_id)
        if not club:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado")
        return club

    def _get_membership_or_404(self, club_id: str, user_id: str) -> Membership:
        membership = self.membership_repo.get_member(club_id, user_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership não encontrada",
            )
        return membership

    def _assert_owner_or_master(self, club_id: str, user: User) -> None:
        club = self._get_club_or_404(club_id)
        if club.owner_id != user.id and user.role != Role.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o dono ou MASTER pode gerenciar membros",
            )
