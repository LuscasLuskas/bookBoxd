from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse
from app.services.tag_service import TagService

router = APIRouter(prefix="/books", tags=["tags"])


@router.post("/{book_id}/tags", response_model=TagResponse, status_code=201)
def add_tag(
    book_id: str,
    body: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona uma tag comunitária a um livro."""
    service = TagService(db)
    tag = service.add_tag(book_id, body.name, current_user)
    db.commit()
    return TagResponse(id=tag.id, name=tag.name, added_by=current_user.id)


@router.delete("/{book_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag(
    book_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove uma tag de um livro (apenas quem a adicionou, ou um master)."""
    TagService(db).remove_tag(book_id, tag_id, current_user)
    db.commit()
