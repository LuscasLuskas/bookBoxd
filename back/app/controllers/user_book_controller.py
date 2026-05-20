from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.user_book import UserBookStatus
from app.schemas.user_book import (
    UserBookAdd,
    UserBookListResponse,
    UserBookResponse,
    UserBookStatsResponse,
    UserBookUpdate,
)
from app.services.user_book_service import UserBookService

router = APIRouter(prefix="/me/books", tags=["user-books"])


@router.post("", response_model=UserBookResponse, status_code=201)
def add_to_library(
    body: UserBookAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona um livro à biblioteca pessoal do usuário."""
    service = UserBookService(db)
    user_book = service.add_book(body.book_id, body.status, current_user)
    db.commit()
    db.refresh(user_book)
    return user_book


@router.get("", response_model=UserBookListResponse)
def list_library(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: UserBookStatus | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista a biblioteca pessoal do usuário com filtro opcional por status."""
    service = UserBookService(db)
    items, total = service.list_books(
        current_user=current_user, limit=limit, offset=offset, status_filter=status
    )
    return UserBookListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/stats", response_model=UserBookStatsResponse)
def library_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna a contagem de livros da biblioteca por status de leitura."""
    service = UserBookService(db)
    return service.get_stats(current_user)


@router.patch("/{book_id}", response_model=UserBookResponse)
def update_book_status(
    book_id: str,
    body: UserBookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o status de leitura de um livro na biblioteca pessoal."""
    service = UserBookService(db)
    user_book = service.update_status(book_id, body.status, current_user)
    db.commit()
    db.refresh(user_book)
    return user_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_library(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove um livro da biblioteca pessoal."""
    service = UserBookService(db)
    service.remove_book(book_id, current_user)
    db.commit()
