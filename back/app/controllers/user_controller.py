from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_master
from app.models.user import User
from app.models.user_book import UserBookStatus
from app.schemas.review import ReviewListResponse
from app.schemas.user import (
    PublicUserResponse,
    UserDeleteResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.user_book import UserBookListResponse, UserBookStatsResponse
from app.services.review_service import ReviewService
from app.services.user_book_service import UserBookService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retorna o perfil do usuário autenticado."""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza nome, bio e livro favorito do usuário autenticado."""
    service = UserService(db)
    user = service.update_profile(current_user, body)
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Faz upload da foto de perfil do usuário autenticado."""
    service = UserService(db)
    user = service.update_avatar(current_user, file)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/me", response_model=UserDeleteResponse, status_code=200)
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deleta a conta do usuário autenticado."""
    service = UserService(db)
    service.delete_account(user=current_user, actor=current_user)
    db.commit()
    return UserDeleteResponse(message="Conta deletada com sucesso")


@router.get("/{user_id}", response_model=PublicUserResponse)
def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perfil público de outro usuário (apenas para quem compartilha clubes ativos)."""
    service = UserService(db)
    return service.get_public_profile(current_user, user_id)


@router.get("/{user_id}/books", response_model=UserBookListResponse)
def list_user_books(
    user_id: str,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: UserBookStatus | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Biblioteca pessoal de outro usuário (gated pela regra de clubes em comum)."""
    service = UserBookService(db)
    items, total = service.list_books_for_user(
        viewer=current_user,
        target_id=user_id,
        limit=limit,
        offset=offset,
        status_filter=status,
    )
    return UserBookListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{user_id}/books/stats", response_model=UserBookStatsResponse)
def get_user_book_stats(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Contagem da biblioteca de outro usuário por status."""
    service = UserBookService(db)
    return service.get_stats_for_user(current_user, user_id)


@router.get("/{user_id}/reviews", response_model=ReviewListResponse)
def list_user_reviews(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Avaliações públicas escritas por outro usuário."""
    service = ReviewService(db)
    return service.list_user_reviews(current_user, user_id)


@router.delete("/{user_id}", response_model=UserDeleteResponse, status_code=200)
def delete_user(
    user_id: str,
    actor: User = Depends(require_master),
    db: Session = Depends(get_db),
):
    """Deleta qualquer usuário (somente MASTER)."""
    from app.repositories.user_repository import UserRepository
    from fastapi import HTTPException

    user_repo = UserRepository(db)
    target = user_repo.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    service = UserService(db)
    service.delete_account(user=target, actor=actor)
    db.commit()
    return UserDeleteResponse(message="Usuário deletado com sucesso")
