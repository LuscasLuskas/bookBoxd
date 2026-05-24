import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_book import UserBook, UserBookStatus
from app.repositories.book_repository import BookRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_book_repository import UserBookRepository
from app.schemas.user_book import UserBookResponse


class UserBookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserBookRepository(db)
        self.book_repo = BookRepository(db)
        self.review_repo = ReviewRepository(db)

    def add_book(self, book_id: str, book_status: UserBookStatus, current_user: User) -> UserBook:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

        existing = self.repo.get_by_user_and_book(current_user.id, book_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Livro já está na sua biblioteca",
            )

        user_book = UserBook(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            book_id=book_id,
            status=book_status,
        )
        return self.repo.create(user_book)

    def update_status(self, book_id: str, new_status: UserBookStatus, current_user: User) -> UserBook:
        user_book = self.repo.get_by_user_and_book(current_user.id, book_id)
        if not user_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado na sua biblioteca",
            )
        user_book.status = new_status
        user_book.updated_at = datetime.now(timezone.utc)
        return self.repo.save(user_book)

    def remove_book(self, book_id: str, current_user: User) -> None:
        user_book = self.repo.get_by_user_and_book(current_user.id, book_id)
        if not user_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado na sua biblioteca",
            )
        self.repo.delete(user_book)

    def list_books(
        self,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
        status_filter: UserBookStatus | None = None,
    ) -> tuple[list[UserBookResponse], int]:
        items, total = self.repo.list_by_user(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status=status_filter,
        )
        ratings = self.review_repo.ratings_for_user_books(
            current_user.id, [ub.book_id for ub in items]
        )
        responses = [
            UserBookResponse(
                id=ub.id,
                user_id=ub.user_id,
                book_id=ub.book_id,
                status=ub.status,
                rating=ratings.get(ub.book_id),
                created_at=ub.created_at,
                updated_at=ub.updated_at,
            )
            for ub in items
        ]
        return responses, total

    def to_response(self, user_book: UserBook) -> UserBookResponse:
        """Wrap a single UserBook with the caller's review rating (if any)."""
        rating = self.review_repo.ratings_for_user_books(
            user_book.user_id, [user_book.book_id]
        ).get(user_book.book_id)
        return UserBookResponse(
            id=user_book.id,
            user_id=user_book.user_id,
            book_id=user_book.book_id,
            status=user_book.status,
            rating=rating,
            created_at=user_book.created_at,
            updated_at=user_book.updated_at,
        )

    def get_stats(self, current_user: User) -> dict[str, int]:
        counts = self.repo.count_by_status(current_user.id)
        return {
            "wishlist": counts.get(UserBookStatus.WISHLIST, 0),
            "added": counts.get(UserBookStatus.ADDED, 0),
            "reading": counts.get(UserBookStatus.READING, 0),
            "completed": counts.get(UserBookStatus.COMPLETED, 0),
            "dropped": counts.get(UserBookStatus.DROPPED, 0),
            "total": sum(counts.values()),
        }
