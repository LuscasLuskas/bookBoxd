from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.interfaces.http.schemas.auth import GoogleLoginRequest, TokenResponse, AuthenticatedUserResponse
from app.application.services.auth_service import AuthService
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/google", response_model=TokenResponse)
async def login_google(request: GoogleLoginRequest, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService()
    try:
        _, token = await auth_service.login_with_google(session, request.id_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {"access_token": token}

@router.get("/me", response_model=AuthenticatedUserResponse)
async def get_me(request: Request):
    user = get_current_user(request)
    return AuthenticatedUserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
    )
