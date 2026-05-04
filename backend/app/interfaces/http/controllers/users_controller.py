from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.application.services.user_service import UserService
from app.interfaces.http.schemas.user import DeleteUserResponse, UserResponse
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    service = UserService()
    user = await service.user_repo.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at
    )

@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(user_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = UserService()
    try:
        await service.delete_user(session, user_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DeleteUserResponse(success=True)
