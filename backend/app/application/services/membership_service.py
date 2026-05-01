from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.membership import Membership
from app.infrastructure.db.repositories.membership_repository import MembershipRepository
from app.domain.enums.membership_status import MembershipStatus


class MembershipService:
    def __init__(self) -> None:
        self.membership_repo = MembershipRepository()

    async def request_join(self, session: AsyncSession, user_id, club_id) -> Membership:
        membership = await self.membership_repo.get_by_user_and_club(session, user_id, club_id)
        now = datetime.utcnow()

        if membership:
            if membership.status == MembershipStatus.KICKED:
                if membership.kicked_until and now < membership.kicked_until:
                    raise ValueError("User is banned from this club until later")
                membership.status = MembershipStatus.PENDING
                membership.kicked_until = None
                return await self.membership_repo.update(session, membership)

            if membership.status == MembershipStatus.ACTIVE:
                raise ValueError("User is already a member of this club")

            if membership.status == MembershipStatus.PENDING:
                return membership

            if membership.status == MembershipStatus.LEFT:
                membership.status = MembershipStatus.PENDING
                membership.kicked_until = None
                return await self.membership_repo.update(session, membership)

        membership = Membership(
            user_id=user_id,
            club_id=club_id,
            status=MembershipStatus.PENDING,
        )
        return await self.membership_repo.create(session, membership)

    async def approve(self, session: AsyncSession, user_id, club_id) -> Membership:
        membership = await self.membership_repo.get_by_user_and_club(session, user_id, club_id)
        if not membership or membership.status != MembershipStatus.PENDING:
            raise ValueError("No pending request found")
        membership.status = MembershipStatus.ACTIVE
        membership.kicked_until = None
        return await self.membership_repo.update(session, membership)

    async def reject(self, session: AsyncSession, user_id, club_id) -> Membership:
        membership = await self.membership_repo.get_by_user_and_club(session, user_id, club_id)
        if not membership or membership.status != MembershipStatus.PENDING:
            raise ValueError("No pending request found")
        membership.status = MembershipStatus.LEFT
        membership.kicked_until = None
        return await self.membership_repo.update(session, membership)

    async def leave(self, session: AsyncSession, user_id, club_id) -> Membership:
        membership = await self.membership_repo.get_by_user_and_club(session, user_id, club_id)
        if not membership or membership.status not in (MembershipStatus.ACTIVE, MembershipStatus.PENDING):
            raise ValueError("Membership cannot be left")
        membership.status = MembershipStatus.LEFT
        membership.kicked_until = None
        return await self.membership_repo.update(session, membership)

    async def ban(self, session: AsyncSession, user_id, club_id, minutes: int) -> Membership:
        membership = await self.membership_repo.get_by_user_and_club(session, user_id, club_id)
        if not membership:
            membership = Membership(user_id=user_id, club_id=club_id, status=MembershipStatus.KICKED)
        membership.status = MembershipStatus.KICKED
        membership.kicked_until = datetime.utcnow() + timedelta(minutes=minutes)
        return await self.membership_repo.create(session, membership)

    async def kick(self, session: AsyncSession, user_id, club_id, minutes: int) -> Membership:
        return await self.ban(session, user_id, club_id, minutes)
