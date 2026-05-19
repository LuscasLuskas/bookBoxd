from sqlalchemy.orm import Session

from app.models.user_book import UserBook, UserBookStatus


class UserBookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_book(self, user_id: str, book_id: str) -> UserBook | None:
        return (
            self.db.query(UserBook)
            .filter(UserBook.user_id == user_id, UserBook.book_id == book_id)
            .first()
        )

    def list_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: UserBookStatus | None = None,
    ) -> tuple[list[UserBook], int]:
        query = self.db.query(UserBook).filter(UserBook.user_id == user_id)
        if status:
            query = query.filter(UserBook.status == status)
        total = query.count()
        items = query.order_by(UserBook.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, user_book: UserBook) -> UserBook:
        self.db.add(user_book)
        self.db.flush()
        self.db.refresh(user_book)
        return user_book

    def save(self, user_book: UserBook) -> UserBook:
        self.db.flush()
        self.db.refresh(user_book)
        return user_book

    def delete(self, user_book: UserBook) -> None:
        self.db.delete(user_book)

    def delete_by_user(self, user_id: str) -> None:
        self.db.query(UserBook).filter(UserBook.user_id == user_id).delete()
