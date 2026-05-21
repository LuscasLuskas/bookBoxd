from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.genre import GenreListResponse
from app.services.genre_service import GenreService

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("", response_model=GenreListResponse)
def list_genres(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos os gêneros do catálogo (para filtros de busca)."""
    return GenreListResponse(items=GenreService(db).list_genres())
