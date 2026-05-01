from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.application.services.membership_service import MembershipService
from app.interfaces.http.schemas.membership import MembershipResponse, MembershipActionResponse
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/clubs/{club_id}/join", response_model=MembershipResponse)
async def join_club(club_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    user = get_current_user(request)
    service = MembershipService()
    membership = await service.request_join(session, user.id, club_id)
    return MembershipResponse(
        id=str(membership.id),
        user_id=str(membership.user_id),
        club_id=str(membership.club_id),
        status=membership.status,
        kicked_until=membership.kicked_until,
        created_at=membership.created_at,
    )

@router.post("/clubs/{club_id}/approve/{user_id}", response_model=MembershipActionResponse)
async def approve_member(club_id: str, user_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = MembershipService()
    try:
        await service.approve(session, user_id, club_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MembershipActionResponse(success=True, message="Member approved")

@router.post("/clubs/{club_id}/reject/{user_id}", response_model=MembershipActionResponse)
async def reject_member(club_id: str, user_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = MembershipService()
    try:
        await service.reject(session, user_id, club_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MembershipActionResponse(success=True, message="Member rejected")

@router.post("/clubs/{club_id}/leave", response_model=MembershipActionResponse)
async def leave_club(club_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    user = get_current_user(request)
    service = MembershipService()
    try:
        await service.leave(session, user.id, club_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MembershipActionResponse(success=True, message="Left club")

@router.post("/clubs/{club_id}/kick/{user_id}", response_model=MembershipActionResponse)
async def kick_member(club_id: str, user_id: str, request: Request, duration_minutes: int = 60, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = MembershipService()
    try:
        await service.kick(session, user_id, club_id, duration_minutes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MembershipActionResponse(success=True, message=f"Member kicked for {duration_minutes} minutes")
