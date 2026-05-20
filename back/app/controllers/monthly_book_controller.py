from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.reading_register import (
    MonthlyBookListResponse,
    MonthlyBookResponse,
    MonthlyBookSet,
    RegisterListResponse,
    RegisterResponse,
    RegisterUpdate,
)
from app.services.monthly_book_service import MonthlyBookService

router = APIRouter(prefix="/clubs", tags=["monthly-book"])


@router.post(
    "/{club_id}/monthly-books", response_model=MonthlyBookResponse, status_code=201
)
def set_monthly_book(
    club_id: str,
    body: MonthlyBookSet,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona um livro do mês ao clube e cria um registro de leitura para cada
    membro ativo (somente owner ou MASTER). O clube pode ter vários ativos."""
    service = MonthlyBookService(db)
    result = service.set_monthly_book(club_id, body.book_id, current_user)
    db.commit()
    return result


@router.get("/{club_id}/monthly-books", response_model=MonthlyBookListResponse)
def list_monthly_books(
    club_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista os livros do mês do clube (ativos e encerrados)."""
    service = MonthlyBookService(db)
    return service.list_monthly_books(club_id, current_user)


@router.get(
    "/{club_id}/monthly-books/{monthly_book_id}", response_model=MonthlyBookResponse
)
def get_monthly_book(
    club_id: str,
    monthly_book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna um livro do mês específico."""
    service = MonthlyBookService(db)
    return service.get_monthly_book(club_id, monthly_book_id, current_user)


@router.delete(
    "/{club_id}/monthly-books/{monthly_book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_monthly_book(
    club_id: str,
    monthly_book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Encerra um livro do mês (somente owner ou MASTER)."""
    service = MonthlyBookService(db)
    service.clear_monthly_book(club_id, monthly_book_id, current_user)
    db.commit()


@router.get(
    "/{club_id}/monthly-books/{monthly_book_id}/registers",
    response_model=RegisterListResponse,
)
def list_registers(
    club_id: str,
    monthly_book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Placar de progresso de todos os membros neste livro do mês."""
    service = MonthlyBookService(db)
    return service.list_registers(club_id, monthly_book_id, current_user)


@router.get(
    "/{club_id}/monthly-books/{monthly_book_id}/register",
    response_model=RegisterResponse,
)
def get_my_register(
    club_id: str,
    monthly_book_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna o registro de leitura pessoal do usuário para este livro do mês."""
    service = MonthlyBookService(db)
    result = service.get_my_register(club_id, monthly_book_id, current_user)
    db.commit()  # pode criar o registro de quem entrou após o set
    return result


@router.patch(
    "/{club_id}/monthly-books/{monthly_book_id}/register",
    response_model=RegisterResponse,
)
def update_my_register(
    club_id: str,
    monthly_book_id: str,
    body: RegisterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o registro pessoal: unidade (página/capítulo), frequência da
    meta (diária/semanal), total e posição atual de leitura."""
    service = MonthlyBookService(db)
    result = service.update_my_register(
        club_id, monthly_book_id, body, current_user
    )
    db.commit()
    return result
