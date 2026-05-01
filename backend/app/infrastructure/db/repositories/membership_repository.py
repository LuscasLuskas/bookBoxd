from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.membership import Membership


class MembershipRepository:
    async def get_by_user_and_club(self, session: AsyncSession, user_id, club_id) -> Optional[Membership]:
        result = await session.execute(
            select(Membership).where(Membership.user_id == user_id, Membership.club_id == club_id)
        )
        return result.scalars().first()

    async def list_active_members_by_club(self, session: AsyncSession, club_id, exclude_user_id=None):
        query = select(Membership).where(
            Membership.club_id == club_id,
            Membership.status == "ACTIVE",
        )
        if exclude_user_id:
            query = query.where(Membership.user_id != exclude_user_id)
        result = await session.execute(query.order_by(Membership.created_at))
        return result.scalars().all()

    async def create(self, session: AsyncSession, membership: Membership) -> Membership:
        session.add(membership)
        await session.flush()
        return membership

    async def update(self, session: AsyncSession, membership: Membership) -> Membership:
        session.add(membership)
        await session.flush()
        return membership

    async def delete_by_user(self, session: AsyncSession, user_id):
        await session.execute(delete(Membership).where(Membership.user_id == user_id))
