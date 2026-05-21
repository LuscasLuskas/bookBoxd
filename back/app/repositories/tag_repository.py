from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.tag import BookTag, Tag


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Tag | None:
        return (
            self.db.query(Tag)
            .filter(func.lower(Tag.name) == name.lower())
            .first()
        )

    def create(self, tag: Tag) -> Tag:
        self.db.add(tag)
        self.db.flush()
        self.db.refresh(tag)
        return tag

    def get_link(self, book_id: str, tag_id: str) -> BookTag | None:
        return (
            self.db.query(BookTag)
            .filter(BookTag.book_id == book_id, BookTag.tag_id == tag_id)
            .first()
        )

    def create_link(self, book_tag: BookTag) -> BookTag:
        self.db.add(book_tag)
        self.db.flush()
        return book_tag

    def delete_link(self, book_tag: BookTag) -> None:
        self.db.delete(book_tag)

    def tags_for_book(self, book_id: str) -> list[tuple[Tag, BookTag]]:
        """Returns (tag, link) pairs for a book, ordered by tag name."""
        return (
            self.db.query(Tag, BookTag)
            .join(BookTag, BookTag.tag_id == Tag.id)
            .filter(BookTag.book_id == book_id)
            .order_by(func.lower(Tag.name))
            .all()
        )
