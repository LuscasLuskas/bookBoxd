import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.club_book import ClubBook
from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.book_repository import BookRepository
from app.repositories.club_book_repository import ClubBookRepository


class ClubBookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClubBookRepository(db)
        self.club_repo = BookClubRepository(db)
        self.book_repo = BookRepository(db)

    def add_book(self, club_id: str, book_id: str, current_user: User) -> ClubBook:
        club = self._get_club_or_404(club_id)
        self._assert_owner_or_master(club, current_user)

        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

        existing = self.repo.get_by_club_and_book(club_id, book_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Livro já adicionado a este clube",
            )

        club_book = ClubBook(
            id=str(uuid.uuid4()),
            club_id=club_id,
            book_id=book_id,
            added_by=current_user.id,
        )
        return self.repo.create(club_book)

    def remove_book(self, club_id: str, book_id: str, current_user: User) -> None:
        club = self._get_club_or_404(club_id)
        self._assert_owner_or_master(club, current_user)

        club_book = self.repo.get_by_club_and_book(club_id, book_id)
        if not club_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado neste clube",
            )
        self.repo.delete(club_book)

    def list_books(
        self, club_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[ClubBook], int]:
        self._get_club_or_404(club_id)
        return self.repo.list_by_club(club_id, limit=limit, offset=offset)

    def _get_club_or_404(self, club_id: str):
        club = self.club_repo.get_by_id(club_id)
        if not club:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado")
        return club

    def _assert_owner_or_master(self, club, user: User) -> None:
        if club.owner_id != user.id and user.role != Role.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o dono ou MASTER pode gerenciar livros do clube",
            )
