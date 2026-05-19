from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.book_club import BookClubCreate, BookClubResponse, BookClubUpdate
from app.services.book_club_service import BookClubService

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.post("", response_model=BookClubResponse, status_code=201)
def create_club(
    body: BookClubCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um novo clube de leitura."""
    service = BookClubService(db)
    club = service.create(body, current_user)
    db.commit()
    db.refresh(club)
    return club


@router.get("/{club_id}", response_model=BookClubResponse)
def get_club(
    club_id: str,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna um clube pelo ID."""
    service = BookClubService(db)
    return service.get_by_id(club_id)


@router.get("", response_model=list[BookClubResponse])
def list_all_clubs(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos os clubes de leitura."""
    service = BookClubService(db)
    return service.list_all()


@router.patch("/{club_id}", response_model=BookClubResponse)
def update_club(
    club_id: str,
    body: BookClubUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza nome/descrição do clube (somente owner ou MASTER)."""
    service = BookClubService(db)
    club = service.update(club_id, body, current_user)
    db.commit()
    db.refresh(club)
    return club


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    club_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deleta o clube (somente owner ou MASTER)."""
    service = BookClubService(db)
    service.delete(club_id, current_user)
    db.commit()
