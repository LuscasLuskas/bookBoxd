import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_book import UserBook, UserBookStatus
from app.repositories.book_repository import BookRepository
from app.repositories.user_book_repository import UserBookRepository


class UserBookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserBookRepository(db)
        self.book_repo = BookRepository(db)

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
    ) -> tuple[list[UserBook], int]:
        return self.repo.list_by_user(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status=status_filter,
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
