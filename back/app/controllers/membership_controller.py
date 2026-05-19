from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.membership import MembershipStatus
from app.models.user import User
from app.schemas.membership import KickRequest, MembershipListResponse, MembershipResponse
from app.services.membership_service import MembershipService

router = APIRouter(prefix="/clubs", tags=["membership"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/{club_id}/join", response_model=MembershipResponse, status_code=200)
@limiter.limit("20/minute")
def join_club(
    request: Request,
    club_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Solicita entrada no clube (cria Membership PENDING). Rate limit: 20 req/min por IP."""
    service = MembershipService(db)
    membership = service.join(club_id, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{club_id}/leave", response_model=MembershipResponse)
def leave_club(
    club_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sai do clube (status → LEFT)."""
    service = MembershipService(db)
    membership = service.leave(club_id, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{club_id}/members/{user_id}/approve", response_model=MembershipResponse)
def approve_member(
    club_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aprova um membro PENDING (somente owner ou MASTER)."""
    service = MembershipService(db)
    membership = service.approve(club_id, user_id, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{club_id}/members/{user_id}/reject", response_model=MembershipResponse)
def reject_member(
    club_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rejeita um membro PENDING (somente owner ou MASTER)."""
    service = MembershipService(db)
    membership = service.reject(club_id, user_id, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{club_id}/members/{user_id}/ban", response_model=MembershipResponse)
def ban_member(
    club_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bane um membro (somente owner ou MASTER). BANNED é estado terminal."""
    service = MembershipService(db)
    membership = service.ban(club_id, user_id, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.post("/{club_id}/members/{user_id}/kick", response_model=MembershipResponse)
def kick_member(
    club_id: str,
    user_id: str,
    body: KickRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Expulsa um membro temporariamente (somente owner ou MASTER)."""
    service = MembershipService(db)
    membership = service.kick(club_id, user_id, body.kicked_until, current_user)
    db.commit()
    db.refresh(membership)
    return membership


@router.get("/{club_id}/members", response_model=MembershipListResponse)
def list_members(
    club_id: str,
    status: MembershipStatus | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista membros do clube com filtro opcional por status."""
    service = MembershipService(db)
    members = service.list_members(club_id, status_filter=status)
    return MembershipListResponse(items=members, total=len(members))
