import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.review_like import ReviewLike
from app.models.user import User
from app.models.user_book import UserBookStatus
from app.repositories.book_repository import BookRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_book_repository import UserBookRepository
from app.schemas.review import (
    ReviewLikeResponse,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpsert,
)

# A review only makes sense once the user has actually read (or given up on) the book.
REVIEWABLE_STATUSES = {UserBookStatus.COMPLETED, UserBookStatus.DROPPED}
# Star values: 0.5–5.0 in half-star steps.
ALLOWED_RATINGS = {round(0.5 * n, 1) for n in range(1, 11)}


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReviewRepository(db)
        self.user_book_repo = UserBookRepository(db)
        self.book_repo = BookRepository(db)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def upsert(self, data: ReviewUpsert, current_user: User) -> ReviewResponse:
        if not self.book_repo.get_by_id(data.book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )

        # Service-layer validation (Pydantic field_validator errors crash the
        # backend with a 500 — see memory note).
        rating = round(data.rating, 1)
        if rating not in ALLOWED_RATINGS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A nota deve ser um múltiplo de 0.5 entre 0.5 e 5.0",
            )

        user_book = self.user_book_repo.get_by_user_and_book(
            current_user.id, data.book_id
        )
        if not user_book or user_book.status not in REVIEWABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Só é possível avaliar livros concluídos ou abandonados na sua biblioteca",
            )

        body = (data.body or "").strip() or None

        review = self.repo.get_by_user_and_book(current_user.id, data.book_id)
        now = datetime.now(timezone.utc)
        if review:
            # First save (review never edited before) shouldn't be flagged as
            # edited; only mark last_edited_at when the row is genuinely modified.
            was_first_save = (
                review.last_edited_at is None and not review.is_deleted
            )
            review.rating = rating
            review.body = body
            review.is_public = data.is_public
            review.is_deleted = False  # un-soft-delete on re-review
            if not was_first_save:
                review.last_edited_at = now
            review.updated_at = now
            review = self.repo.save(review)
        else:
            review = self.repo.create(
                Review(
                    id=str(uuid.uuid4()),
                    user_id=current_user.id,
                    book_id=data.book_id,
                    rating=rating,
                    body=body,
                    is_public=data.is_public,
                )
            )

        return self._review_response(review, current_user.id)

    def delete(self, book_id: str, current_user: User) -> None:
        """Soft-delete: keep the row so a placeholder still renders in the
        public list, and so the author can re-review later."""
        review = self.repo.get_by_user_and_book(current_user.id, book_id)
        if not review or review.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você ainda não escreveu uma avaliação para este livro",
            )
        review.is_deleted = True
        review.body = None
        self.repo.save(review)

    def toggle_like(self, review_id: str, current_user: User) -> ReviewLikeResponse:
        review = self.repo.get_by_id(review_id)
        if not review or review.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada"
            )
        if not review.is_public and review.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta avaliação é privada",
            )

        existing = self.repo.get_like(review_id, current_user.id)
        if existing:
            self.repo.delete_like(existing)
            liked = False
        else:
            self.repo.add_like(
                ReviewLike(review_id=review_id, user_id=current_user.id)
            )
            liked = True

        self.db.flush()
        count = self.repo.likes_count_for_reviews([review_id]).get(review_id, 0)
        return ReviewLikeResponse(review_id=review_id, liked=liked, likes_count=count)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_my_review(self, book_id: str, current_user: User) -> ReviewResponse | None:
        review = self.repo.get_by_user_and_book(current_user.id, book_id)
        if not review or review.is_deleted:
            # Treat soft-deleted as "no review" for the author so the editor
            # re-opens fresh.
            return None
        return self._review_response(review, current_user.id)

    def list_book_reviews(
        self, book_id: str, current_user: User
    ) -> ReviewListResponse:
        if not self.book_repo.get_by_id(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )
        reviews = self.repo.list_public_for_book(book_id)
        items = self._batch_to_responses(reviews, current_user.id)
        return ReviewListResponse(items=items, total=len(items))

    def list_user_reviews(
        self, viewer: User, target_id: str
    ) -> ReviewListResponse:
        """Public, non-deleted reviews written by `target_id`, enriched with book info."""
        from app.core.access import assert_can_view_user

        assert_can_view_user(self.db, viewer, target_id)
        reviews = self.repo.list_public_for_user(target_id)
        items = self._batch_to_responses(reviews, viewer.id, include_book=True)
        return ReviewListResponse(items=items, total=len(items))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _review_response(self, review: Review, viewer_id: str) -> ReviewResponse:
        return self._batch_to_responses([review], viewer_id)[0]

    def _batch_to_responses(
        self,
        reviews: list[Review],
        viewer_id: str,
        include_book: bool = False,
    ) -> list[ReviewResponse]:
        if not reviews:
            return []
        # Likes/like-state only apply to live reviews — deleted rows have no
        # interactive footprint.
        live_ids = [r.id for r in reviews if not r.is_deleted]
        likes = self.repo.likes_count_for_reviews(live_ids)
        liked = self.repo.liked_by_user(viewer_id, live_ids)
        return [self._build_response(r, likes, liked, include_book) for r in reviews]

    def _build_response(
        self,
        review: Review,
        likes: dict[str, int],
        liked: set[str],
        include_book: bool = False,
    ) -> ReviewResponse:
        book_title = review.book.title if include_book and review.book else None
        book_cover_url = (
            review.book.cover_url if include_book and review.book else None
        )
        if review.is_deleted:
            # Strip identifying info so the placeholder is anonymous.
            return ReviewResponse(
                id=review.id,
                user_id=None,
                user_name=None,
                user_avatar_url=None,
                book_id=review.book_id,
                book_title=book_title,
                book_cover_url=book_cover_url,
                rating=None,
                body=None,
                is_public=review.is_public,
                is_deleted=True,
                is_edited=False,
                likes_count=0,
                liked_by_me=False,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
        return ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.user.name if review.user else None,
            user_avatar_url=review.user.avatar_url if review.user else None,
            book_id=review.book_id,
            book_title=book_title,
            book_cover_url=book_cover_url,
            rating=review.rating,
            body=review.body,
            is_public=review.is_public,
            is_deleted=False,
            is_edited=review.last_edited_at is not None,
            likes_count=likes.get(review.id, 0),
            liked_by_me=review.id in liked,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
