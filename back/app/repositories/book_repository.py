from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.book import Book


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, book_id: str) -> Book | None:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def list(
        self,
        limit: int = 20,
        offset: int = 0,
        title: str | None = None,
        author: str | None = None,
    ) -> tuple[list[Book], int]:
        query = self.db.query(Book)
        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        total = query.count()
        items = query.order_by(Book.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, book: Book) -> Book:
        self.db.add(book)
        self.db.flush()
        self.db.refresh(book)
        return book

    def nullify_created_by(self, user_id: str, name_snapshot: str) -> None:
        self.db.query(Book).filter(Book.created_by == user_id).update(
            {
                "created_by": None,
                "created_by_name_snapshot": f"{name_snapshot} (deleted account)",
            }
        )
