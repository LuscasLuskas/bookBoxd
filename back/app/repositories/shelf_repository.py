from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.shelf import Shelf, ShelfBook


class ShelfRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: str) -> list[Shelf]:
        return (
            self.db.query(Shelf)
            .filter(Shelf.user_id == user_id)
            .order_by(Shelf.created_at.desc())
            .all()
        )

    def get(self, shelf_id: str) -> Shelf | None:
        return self.db.query(Shelf).filter(Shelf.id == shelf_id).first()

    def get_by_user_and_name(self, user_id: str, name: str) -> Shelf | None:
        return (
            self.db.query(Shelf)
            .filter(Shelf.user_id == user_id, func.lower(Shelf.name) == name.lower())
            .first()
        )

    def create(self, shelf: Shelf) -> Shelf:
        self.db.add(shelf)
        self.db.flush()
        self.db.refresh(shelf)
        return shelf

    def delete(self, shelf: Shelf) -> None:
        self.db.delete(shelf)

    def book_counts(self, shelf_ids: list[str]) -> dict[str, int]:
        """Maps each shelf id to its book count in a single query."""
        if not shelf_ids:
            return {}
        rows = (
            self.db.query(ShelfBook.shelf_id, func.count(ShelfBook.book_id))
            .filter(ShelfBook.shelf_id.in_(shelf_ids))
            .group_by(ShelfBook.shelf_id)
            .all()
        )
        return {shelf_id: count for shelf_id, count in rows}

    def get_shelf_book(self, shelf_id: str, book_id: str) -> ShelfBook | None:
        return (
            self.db.query(ShelfBook)
            .filter(ShelfBook.shelf_id == shelf_id, ShelfBook.book_id == book_id)
            .first()
        )

    def add_book(self, shelf_book: ShelfBook) -> ShelfBook:
        self.db.add(shelf_book)
        self.db.flush()
        return shelf_book

    def remove_book(self, shelf_book: ShelfBook) -> None:
        self.db.delete(shelf_book)

    def books_in_shelf(self, shelf_id: str) -> list[Book]:
        return (
            self.db.query(Book)
            .join(ShelfBook, ShelfBook.book_id == Book.id)
            .filter(ShelfBook.shelf_id == shelf_id)
            .order_by(ShelfBook.created_at.desc())
            .all()
        )
