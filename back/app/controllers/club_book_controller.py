from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.club_book import ClubBookAdd, ClubBookListResponse, ClubBookResponse
from app.services.club_book_service import ClubBookService

router = APIRouter(prefix="/clubs", tags=["club-books"])


@router.post("/{club_id}/books", response_model=ClubBookResponse, status_code=201)
def add_book_to_club(
    club_id: str,
    body: ClubBookAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona um livro ao catálogo do clube (somente owner ou MASTER)."""
    service = ClubBookService(db)
    club_book = service.add_book(club_id, body.book_id, current_user)
    db.commit()
    db.refresh(club_book)
    return club_book


@router.get("/{club_id}/books", response_model=ClubBookListResponse)
def list_club_books(
    club_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista livros do clube."""
    service = ClubBookService(db)
    items, total = service.list_books(club_id, limit=limit, offset=offset)
    return ClubBookListResponse(items=items, total=total, limit=limit, offset=offset)


@router.delete("/{club_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book_from_club(
    club_id: str,
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove um livro do catálogo do clube (somente owner ou MASTER)."""
    service = ClubBookService(db)
    service.remove_book(club_id, book_id, current_user)
    db.commit()
