from app.infrastructure.db.models.access_log import AccessLog
from sqlalchemy.ext.asyncio import AsyncSession


class AccessLogRepository:
    async def create(self, session: AsyncSession, log: AccessLog) -> AccessLog:
        session.add(log)
        await session.flush()
        return log
