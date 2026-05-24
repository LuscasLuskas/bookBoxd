import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book_club import BookClub
from app.models.forum_post import ForumPost
from app.models.forum_thread import ForumThread
from app.models.membership import MembershipStatus
from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.book_repository import BookRepository
from app.repositories.forum_repository import ForumRepository
from app.repositories.membership_repository import MembershipRepository
from app.schemas.forum import (
    ForumPostCreate,
    ForumPostResponse,
    ForumPostUpdate,
    ForumThreadCreate,
    ForumThreadDetailResponse,
    ForumThreadListResponse,
    ForumThreadResponse,
)


class ForumService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ForumRepository(db)
        self.club_repo = BookClubRepository(db)
        self.book_repo = BookRepository(db)
        self.membership_repo = MembershipRepository(db)

    # ------------------------- Threads -------------------------

    def list_threads(
        self, club_id: str, current_user: User
    ) -> ForumThreadListResponse:
        club = self._get_club_or_404(club_id)
        self._assert_member_or_manager(club, current_user)
        threads = self.repo.list_threads_for_club(club_id)
        counts = self.repo.posts_count_for_threads([t.id for t in threads])
        items = [self._thread_response(t, counts.get(t.id, 0)) for t in threads]
        return ForumThreadListResponse(items=items, total=len(items))

    def get_thread(
        self, club_id: str, thread_id: str, current_user: User
    ) -> ForumThreadDetailResponse:
        club = self._get_club_or_404(club_id)
        self._assert_member_or_manager(club, current_user)
        thread = self._get_thread_in_club_or_404(club_id, thread_id)
        posts = self.repo.list_posts(thread.id)
        base = self._thread_response(thread, len(posts))
        return ForumThreadDetailResponse(
            **base.model_dump(),
            posts=[self._post_response(p) for p in posts],
        )

    def create_thread(
        self, club_id: str, data: ForumThreadCreate, current_user: User
    ) -> ForumThreadResponse:
        club = self._get_club_or_404(club_id)
        self._assert_active_member_or_owner(club, current_user)
        title = data.title.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Título obrigatório"
            )
        if data.book_id and not self.book_repo.get_by_id(data.book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )

        thread = self.repo.create_thread(
            ForumThread(
                id=str(uuid.uuid4()),
                club_id=club_id,
                book_id=data.book_id,
                title=title[:255],
                is_pinned=False,
                auto_created=False,
                created_by=current_user.id,
            )
        )
        return self._thread_response(thread, 0)

    def delete_thread(
        self, club_id: str, thread_id: str, current_user: User
    ) -> None:
        club = self._get_club_or_404(club_id)
        thread = self._get_thread_in_club_or_404(club_id, thread_id)
        is_owner = club.owner_id == current_user.id
        is_master = current_user.role == Role.MASTER
        is_creator = thread.created_by == current_user.id
        if not (is_owner or is_master or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o autor, o dono do clube ou MASTER pode apagar a thread",
            )
        self.repo.delete_thread(thread)

    # ------------------------- Posts -------------------------

    def create_post(
        self,
        club_id: str,
        thread_id: str,
        data: ForumPostCreate,
        current_user: User,
    ) -> ForumPostResponse:
        club = self._get_club_or_404(club_id)
        self._assert_active_member_or_owner(club, current_user)
        thread = self._get_thread_in_club_or_404(club_id, thread_id)
        body = data.body.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagem não pode ser vazia",
            )
        post = self.repo.create_post(
            ForumPost(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                user_id=current_user.id,
                body=body[:10000],
            )
        )
        return self._post_response(post)

    def update_post(
        self,
        club_id: str,
        thread_id: str,
        post_id: str,
        data: ForumPostUpdate,
        current_user: User,
    ) -> ForumPostResponse:
        self._get_club_or_404(club_id)
        self._get_thread_in_club_or_404(club_id, thread_id)
        post = self._get_post_in_thread_or_404(thread_id, post_id)
        if post.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta mensagem foi excluída",
            )
        if post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o autor pode editar esta mensagem",
            )
        body = data.body.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagem não pode ser vazia",
            )
        post.body = body[:10000]
        post.last_edited_at = datetime.now(timezone.utc)
        post = self.repo.save_post(post)
        return self._post_response(post)

    def delete_post(
        self,
        club_id: str,
        thread_id: str,
        post_id: str,
        current_user: User,
    ) -> None:
        """Soft-delete: author, club owner, or MASTER may remove. The row
        stays so a placeholder still renders in the thread."""
        club = self._get_club_or_404(club_id)
        self._get_thread_in_club_or_404(club_id, thread_id)
        post = self._get_post_in_thread_or_404(thread_id, post_id)
        if post.is_deleted:
            return  # Idempotent: deleting an already-excluded post is a no-op.
        is_author = post.user_id == current_user.id
        is_owner = club.owner_id == current_user.id
        is_master = current_user.role == Role.MASTER
        if not (is_author or is_owner or is_master):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o autor, o dono do clube ou MASTER pode excluir esta mensagem",
            )
        post.is_deleted = True
        self.repo.save_post(post)

    # ------------------------- Auto-pin hooks -------------------------

    def on_monthly_book_set(
        self,
        club_id: str,
        book_id: str,
        book_title: str,
        actor: User,
    ) -> ForumThread:
        """Open (or repin) a pinned thread for a club's new monthly book."""
        existing = self.repo.find_auto_thread_for_book(club_id, book_id)
        if existing:
            existing.is_pinned = True
            return self.repo.save_thread(existing)
        return self.repo.create_thread(
            ForumThread(
                id=str(uuid.uuid4()),
                club_id=club_id,
                book_id=book_id,
                title=f"Reading discussion: {book_title}"[:255],
                is_pinned=True,
                auto_created=True,
                created_by=actor.id,
            )
        )

    def on_monthly_book_cleared(self, club_id: str, book_id: str) -> None:
        """Unpin the auto-created thread when a club ends its monthly book."""
        existing = self.repo.find_auto_thread_for_book(club_id, book_id)
        if existing and existing.is_pinned:
            existing.is_pinned = False
            self.repo.save_thread(existing)

    # ------------------------- Helpers -------------------------

    def _thread_response(
        self, thread: ForumThread, posts_count: int
    ) -> ForumThreadResponse:
        return ForumThreadResponse(
            id=thread.id,
            club_id=thread.club_id,
            book_id=thread.book_id,
            book_title=thread.book.title if thread.book else None,
            book_cover_url=thread.book.cover_url if thread.book else None,
            title=thread.title,
            is_pinned=thread.is_pinned,
            auto_created=thread.auto_created,
            created_by=thread.created_by,
            created_by_name=thread.creator.name if thread.creator else None,
            posts_count=posts_count,
            created_at=thread.created_at,
        )

    def _post_response(self, post: ForumPost) -> ForumPostResponse:
        if post.is_deleted:
            # Strip identifying info so the placeholder is anonymous.
            return ForumPostResponse(
                id=post.id,
                thread_id=post.thread_id,
                user_id=None,
                user_name=None,
                user_avatar_url=None,
                body="",
                is_deleted=True,
                is_edited=False,
                created_at=post.created_at,
            )
        return ForumPostResponse(
            id=post.id,
            thread_id=post.thread_id,
            user_id=post.user_id,
            user_name=post.user.name if post.user else None,
            user_avatar_url=post.user.avatar_url if post.user else None,
            body=post.body,
            is_deleted=False,
            is_edited=post.last_edited_at is not None,
            created_at=post.created_at,
        )

    def _get_club_or_404(self, club_id: str) -> BookClub:
        club = self.club_repo.get_by_id(club_id)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado"
            )
        return club

    def _get_thread_in_club_or_404(
        self, club_id: str, thread_id: str
    ) -> ForumThread:
        thread = self.repo.get_thread(thread_id)
        if not thread or thread.club_id != club_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tópico do fórum não encontrado",
            )
        return thread

    def _get_post_in_thread_or_404(
        self, thread_id: str, post_id: str
    ) -> ForumPost:
        post = self.repo.get_post(post_id)
        if not post or post.thread_id != thread_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem não encontrada",
            )
        return post

    def _assert_member_or_manager(self, club: BookClub, user: User) -> None:
        if club.owner_id == user.id or user.role == Role.MASTER:
            return
        membership = self.membership_repo.get_by_user_and_club(user.id, club.id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas membros do clube podem ver o fórum",
            )

    def _assert_active_member_or_owner(self, club: BookClub, user: User) -> None:
        if club.owner_id == user.id or user.role == Role.MASTER:
            return
        membership = self.membership_repo.get_by_user_and_club(user.id, club.id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas membros ativos podem postar no fórum",
            )
