from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_master
from app.models.user import User
from app.schemas.user import UserDeleteResponse, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retorna o perfil do usuário autenticado."""
    return current_user


@router.delete("/me", response_model=UserDeleteResponse, status_code=200)
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deleta a conta do usuário autenticado."""
    service = UserService(db)
    service.delete_account(user=current_user, actor=current_user)
    db.commit()
    return UserDeleteResponse(message="Conta deletada com sucesso")


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
