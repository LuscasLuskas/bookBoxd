from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import (
    ReviewLikeResponse,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpsert,
)
from app.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/me/reviews", response_model=ReviewResponse)
def upsert_review(
    body: ReviewUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria ou atualiza a avaliação do usuário para um livro (nota + texto opcional)."""
    service = ReviewService(db)
    result = service.upsert(body, current_user)
    db.commit()
    return result


@router.get("/me/reviews/{book_id}", response_model=ReviewResponse)
def get_my_review(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna a avaliação do usuário para um livro (404 se não houver)."""
    service = ReviewService(db)
    result = service.get_my_review(book_id, current_user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Você ainda não avaliou este livro",
        )
    return result


@router.delete("/me/reviews/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_review(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apaga a avaliação do usuário para um livro."""
    service = ReviewService(db)
    service.delete(book_id, current_user)
    db.commit()


@router.get("/books/{book_id}/reviews", response_model=ReviewListResponse)
def list_book_reviews(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista as avaliações públicas de um livro, ordenadas da mais recente."""
    service = ReviewService(db)
    return service.list_book_reviews(book_id, current_user)


@router.post("/reviews/{review_id}/like", response_model=ReviewLikeResponse)
def toggle_like(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Curte ou descurte uma avaliação."""
    service = ReviewService(db)
    result = service.toggle_like(review_id, current_user)
    db.commit()
    return result
