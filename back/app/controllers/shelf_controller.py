from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.shelf import (
    ShelfBookAdd,
    ShelfCreate,
    ShelfDetailResponse,
    ShelfListResponse,
    ShelfResponse,
)
from app.services.shelf_service import ShelfService

router = APIRouter(prefix="/me/shelves", tags=["shelves"])


@router.get("", response_model=ShelfListResponse)
def list_shelves(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista as estantes (coleções personalizadas) do usuário."""
    return ShelfListResponse(items=ShelfService(db).list_shelves(current_user))


@router.post("", response_model=ShelfResponse, status_code=201)
def create_shelf(
    body: ShelfCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria uma nova estante."""
    service = ShelfService(db)
    shelf = service.create_shelf(body.name, current_user)
    db.commit()
    return shelf


@router.get("/{shelf_id}", response_model=ShelfDetailResponse)
def get_shelf(
    shelf_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna uma estante com os livros que ela contém."""
    return ShelfService(db).get_shelf_detail(shelf_id, current_user)


@router.delete("/{shelf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shelf(
    shelf_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exclui uma estante (não remove os livros do catálogo)."""
    service = ShelfService(db)
    service.delete_shelf(shelf_id, current_user)
    db.commit()


@router.post("/{shelf_id}/books", response_model=ShelfResponse, status_code=201)
def add_book_to_shelf(
    shelf_id: str,
    body: ShelfBookAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona um livro a uma estante."""
    service = ShelfService(db)
    shelf = service.add_book(shelf_id, body.book_id, current_user)
    db.commit()
    return shelf


@router.delete(
    "/{shelf_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_book_from_shelf(
    shelf_id: str,
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove um livro de uma estante."""
    service = ShelfService(db)
    service.remove_book(shelf_id, book_id, current_user)
    db.commit()
