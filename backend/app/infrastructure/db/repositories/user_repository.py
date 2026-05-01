from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.user import User


class UserRepository:
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_oauth(self, session: AsyncSession, provider: str, oauth_id: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.oauth_provider == provider, User.oauth_id == oauth_id)
        )
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id) -> Optional[User]:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create(self, session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.flush()
        return user

    async def delete(self, session: AsyncSession, user: User) -> None:
        await session.delete(user)
