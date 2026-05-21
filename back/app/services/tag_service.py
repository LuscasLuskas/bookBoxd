import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tag import BookTag, Tag
from app.models.user import Role, User
from app.repositories.book_repository import BookRepository
from app.repositories.tag_repository import TagRepository


class TagService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TagRepository(db)
        self.book_repo = BookRepository(db)

    def list_tags(self, book_id: str) -> list[tuple[Tag, BookTag]]:
        return self.repo.tags_for_book(book_id)

    def add_tag(self, book_id: str, name: str, current_user: User) -> Tag:
        if not self.book_repo.get_by_id(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )
        name = name.strip()[:50]
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A tag não pode ser vazia",
            )

        tag = self.repo.get_by_name(name)
        if not tag:
            tag = self.repo.create(Tag(id=str(uuid.uuid4()), name=name))

        if self.repo.get_link(book_id, tag.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Essa tag já foi adicionada a este livro",
            )
        self.repo.create_link(
            BookTag(book_id=book_id, tag_id=tag.id, added_by=current_user.id)
        )
        return tag

    def remove_tag(self, book_id: str, tag_id: str, current_user: User) -> None:
        link = self.repo.get_link(book_id, tag_id)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag não encontrada neste livro",
            )
        # Community tags: removable by whoever applied it, or by a master.
        if link.added_by != current_user.id and current_user.role != Role.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode remover tags que adicionou",
            )
        self.repo.delete_link(link)
