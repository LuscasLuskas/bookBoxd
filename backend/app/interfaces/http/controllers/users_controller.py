from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.application.services.user_service import UserService
from app.interfaces.http.schemas.user import DeleteUserResponse
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(user_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = UserService()
    try:
        await service.delete_user(session, user_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DeleteUserResponse(success=True)
