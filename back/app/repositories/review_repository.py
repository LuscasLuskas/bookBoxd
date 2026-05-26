from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.review import Review
from app.models.review_like import ReviewLike


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: str) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_user_and_book(self, user_id: str, book_id: str) -> Review | None:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id, Review.book_id == book_id)
            .first()
        )

    def list_public_for_book(self, book_id: str) -> list[Review]:
        return (
            self.db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.book_id == book_id, Review.is_public.is_(True))
            .order_by(Review.created_at.desc())
            .all()
        )

    def list_public_for_user(self, user_id: str) -> list[Review]:
        return (
            self.db.query(Review)
            .options(joinedload(Review.user), joinedload(Review.book))
            .filter(
                Review.user_id == user_id,
                Review.is_public.is_(True),
                Review.is_deleted.is_(False),
            )
            .order_by(Review.created_at.desc())
            .all()
        )

    def rating_stats_for_books(
        self, book_ids: list[str]
    ) -> dict[str, tuple[float, int]]:
        """Average rating + count per book, ignoring soft-deleted reviews."""
        if not book_ids:
            return {}
        rows = (
            self.db.query(Review.book_id, func.avg(Review.rating), func.count(Review.id))
            .filter(Review.book_id.in_(book_ids), Review.is_deleted.is_(False))
            .group_by(Review.book_id)
            .all()
        )
        return {book_id: (float(avg), int(count)) for book_id, avg, count in rows}

    def ratings_for_user_books(
        self, user_id: str, book_ids: list[str]
    ) -> dict[str, float]:
        """Caller's own rating for a batch of books (used to enrich library list)."""
        if not book_ids:
            return {}
        rows = (
            self.db.query(Review.book_id, Review.rating)
            .filter(
                Review.user_id == user_id,
                Review.book_id.in_(book_ids),
                Review.is_deleted.is_(False),
            )
            .all()
        )
        return {book_id: float(rating) for book_id, rating in rows}

    def likes_count_for_reviews(self, review_ids: list[str]) -> dict[str, int]:
        if not review_ids:
            return {}
        rows = (
            self.db.query(ReviewLike.review_id, func.count(ReviewLike.user_id))
            .filter(ReviewLike.review_id.in_(review_ids))
            .group_by(ReviewLike.review_id)
            .all()
        )
        return {review_id: int(count) for review_id, count in rows}

    def liked_by_user(self, user_id: str, review_ids: list[str]) -> set[str]:
        if not review_ids:
            return set()
        rows = (
            self.db.query(ReviewLike.review_id)
            .filter(
                ReviewLike.user_id == user_id, ReviewLike.review_id.in_(review_ids)
            )
            .all()
        )
        return {row[0] for row in rows}

    def get_like(self, review_id: str, user_id: str) -> ReviewLike | None:
        return (
            self.db.query(ReviewLike)
            .filter(
                ReviewLike.review_id == review_id, ReviewLike.user_id == user_id
            )
            .first()
        )

    def add_like(self, like: ReviewLike) -> ReviewLike:
        self.db.add(like)
        self.db.flush()
        return like

    def delete_like(self, like: ReviewLike) -> None:
        self.db.delete(like)

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.flush()
        self.db.refresh(review)
        return review

    def save(self, review: Review) -> Review:
        self.db.flush()
        self.db.refresh(review)
        return review

    def delete(self, review: Review) -> None:
        self.db.delete(review)
