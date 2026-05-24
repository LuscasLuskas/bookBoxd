from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.forum import (
    ForumPostCreate,
    ForumPostResponse,
    ForumPostUpdate,
    ForumThreadCreate,
    ForumThreadDetailResponse,
    ForumThreadListResponse,
    ForumThreadResponse,
)
from app.services.forum_service import ForumService

router = APIRouter(prefix="/clubs", tags=["forum"])


@router.get("/{club_id}/forum/threads", response_model=ForumThreadListResponse)
def list_threads(
    club_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista as threads do fórum do clube (pinadas primeiro, depois mais recentes)."""
    service = ForumService(db)
    return service.list_threads(club_id, current_user)


@router.post(
    "/{club_id}/forum/threads", response_model=ForumThreadResponse, status_code=201
)
def create_thread(
    club_id: str,
    body: ForumThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um novo tópico de discussão no fórum do clube (apenas membros ativos)."""
    service = ForumService(db)
    result = service.create_thread(club_id, body, current_user)
    db.commit()
    return result


@router.get(
    "/{club_id}/forum/threads/{thread_id}", response_model=ForumThreadDetailResponse
)
def get_thread(
    club_id: str,
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna um tópico do fórum com suas mensagens."""
    service = ForumService(db)
    return service.get_thread(club_id, thread_id, current_user)


@router.delete(
    "/{club_id}/forum/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_thread(
    club_id: str,
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apaga um tópico (autor, owner do clube ou MASTER)."""
    service = ForumService(db)
    service.delete_thread(club_id, thread_id, current_user)
    db.commit()


@router.post(
    "/{club_id}/forum/threads/{thread_id}/posts",
    response_model=ForumPostResponse,
    status_code=201,
)
def create_post(
    club_id: str,
    thread_id: str,
    body: ForumPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posta uma mensagem em um tópico do fórum."""
    service = ForumService(db)
    result = service.create_post(club_id, thread_id, body, current_user)
    db.commit()
    return result


@router.patch(
    "/{club_id}/forum/threads/{thread_id}/posts/{post_id}",
    response_model=ForumPostResponse,
)
def update_post(
    club_id: str,
    thread_id: str,
    post_id: str,
    body: ForumPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edita uma mensagem do fórum (apenas o autor)."""
    service = ForumService(db)
    result = service.update_post(club_id, thread_id, post_id, body, current_user)
    db.commit()
    return result


@router.delete(
    "/{club_id}/forum/threads/{thread_id}/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    club_id: str,
    thread_id: str,
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete de uma mensagem (autor, dono do clube ou MASTER)."""
    service = ForumService(db)
    service.delete_post(club_id, thread_id, post_id, current_user)
    db.commit()
