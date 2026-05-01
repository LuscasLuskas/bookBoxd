import os
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.auth.jwt import decode_access_token
from app.infrastructure.db.session import async_session
from app.infrastructure.db.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth: Optional[HTTPAuthorizationCredentials] = await security.__call__(request)
        request.state.user = None

        if auth and auth.scheme.lower() == "bearer":
            try:
                payload = decode_access_token(auth.credentials)
                user_id = payload.get("sub")
            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid authorization token")

            async with async_session() as session:
                user = await UserRepository().get_by_id(session, user_id)
                request.state.user = user

        return await call_next(request)


def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
