from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.forum_post import ForumPost
from app.models.forum_thread import ForumThread


class ForumRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------- Threads -------------------------

    def get_thread(self, thread_id: str) -> ForumThread | None:
        return (
            self.db.query(ForumThread)
            .options(joinedload(ForumThread.book), joinedload(ForumThread.creator))
            .filter(ForumThread.id == thread_id)
            .first()
        )

    def list_threads_for_club(self, club_id: str) -> list[ForumThread]:
        return (
            self.db.query(ForumThread)
            .options(joinedload(ForumThread.book), joinedload(ForumThread.creator))
            .filter(ForumThread.club_id == club_id)
            .order_by(ForumThread.is_pinned.desc(), ForumThread.created_at.desc())
            .all()
        )

    def find_auto_thread_for_book(
        self, club_id: str, book_id: str
    ) -> ForumThread | None:
        return (
            self.db.query(ForumThread)
            .filter(
                ForumThread.club_id == club_id,
                ForumThread.book_id == book_id,
                ForumThread.auto_created.is_(True),
            )
            .first()
        )

    def create_thread(self, thread: ForumThread) -> ForumThread:
        self.db.add(thread)
        self.db.flush()
        self.db.refresh(thread)
        return thread

    def save_thread(self, thread: ForumThread) -> ForumThread:
        self.db.flush()
        self.db.refresh(thread)
        return thread

    def delete_thread(self, thread: ForumThread) -> None:
        self.db.delete(thread)

    def posts_count_for_threads(self, thread_ids: list[str]) -> dict[str, int]:
        if not thread_ids:
            return {}
        rows = (
            self.db.query(ForumPost.thread_id, func.count(ForumPost.id))
            .filter(ForumPost.thread_id.in_(thread_ids))
            .group_by(ForumPost.thread_id)
            .all()
        )
        return {tid: int(count) for tid, count in rows}

    # ------------------------- Posts -------------------------

    def get_post(self, post_id: str) -> ForumPost | None:
        return (
            self.db.query(ForumPost)
            .options(joinedload(ForumPost.user))
            .filter(ForumPost.id == post_id)
            .first()
        )

    def list_posts(self, thread_id: str) -> list[ForumPost]:
        # Deleted posts stay in the list so the placeholder renders inline.
        return (
            self.db.query(ForumPost)
            .options(joinedload(ForumPost.user))
            .filter(ForumPost.thread_id == thread_id)
            .order_by(ForumPost.created_at.asc())
            .all()
        )

    def create_post(self, post: ForumPost) -> ForumPost:
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def save_post(self, post: ForumPost) -> ForumPost:
        self.db.flush()
        self.db.refresh(post)
        return post
