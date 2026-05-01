from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.application.services.club_service import ClubService
from app.interfaces.http.schemas.book_club import ClubCreateRequest, ClubResponse
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=ClubResponse)
async def create_club(request_body: ClubCreateRequest, request: Request, session: AsyncSession = Depends(get_session)):
    user = get_current_user(request)
    service = ClubService()
    club = await service.create_club(session, user, request_body.name, request_body.description)
    return ClubResponse(
        id=str(club.id),
        name=club.name,
        description=club.description,
        owner_id=str(club.owner_id),
        created_at=club.created_at,
    )

@router.delete("/{club_id}")
async def delete_club(club_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = ClubService()
    try:
        await service.delete_club(session, club_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True}

@router.post("/{club_id}/transfer/{new_owner_id}")
async def transfer_ownership(club_id: str, new_owner_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    get_current_user(request)
    service = ClubService()
    try:
        club = await service.transfer_ownership(session, club_id, new_owner_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ClubResponse(
        id=str(club.id),
        name=club.name,
        description=club.description,
        owner_id=str(club.owner_id),
        created_at=club.created_at,
    )
