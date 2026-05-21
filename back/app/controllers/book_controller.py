from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.book import (
    BookCreate,
    BookDetailResponse,
    BookListResponse,
    BookResponse,
    ExternalSearchResponse,
)
from app.services.book_service import BookService
from app.services.open_library_service import OpenLibraryService

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookResponse, status_code=201)
def create_book(
    body: BookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um livro no catálogo global."""
    service = BookService(db)
    book = service.create(body, current_user)
    db.commit()
    db.refresh(book)
    return service.enrich_books([book])[0]


@router.get("", response_model=BookListResponse)
def list_books(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    title: str | None = Query(None),
    author: str | None = Query(None),
    genre: str | None = Query(None, description="Filtra por nome de gênero"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista livros do catálogo global com filtros opcionais."""
    service = BookService(db)
    items, total = service.list_books(
        limit=limit, offset=offset, title=title, author=author, genre=genre
    )
    return BookListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/search-external", response_model=ExternalSearchResponse)
def search_external_books(
    q: str = Query(..., min_length=1, description="Termo de busca na Open Library"),
    limit: int = Query(20, ge=1, le=40),
    current_user: User = Depends(get_current_user),
):
    """Busca livros na Open Library (não persiste nada no catálogo)."""
    results = OpenLibraryService().search(q, limit=limit)
    return ExternalSearchResponse(items=results)


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna um livro pelo ID, com avaliação média, gêneros e tags."""
    service = BookService(db)
    return service.get_book_detail(book_id)
