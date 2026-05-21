import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.shelf import Shelf, ShelfBook
from app.models.user import User
from app.repositories.book_repository import BookRepository
from app.repositories.shelf_repository import ShelfRepository
from app.schemas.shelf import ShelfDetailResponse, ShelfResponse
from app.services.book_service import BookService


class ShelfService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ShelfRepository(db)
        self.book_repo = BookRepository(db)

    def _owned_shelf(self, shelf_id: str, current_user: User) -> Shelf:
        shelf = self.repo.get(shelf_id)
        # A 404 (rather than 403) avoids leaking the existence of others' shelves.
        if not shelf or shelf.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Estante não encontrada"
            )
        return shelf

    @staticmethod
    def _to_response(shelf: Shelf, book_count: int) -> ShelfResponse:
        resp = ShelfResponse.model_validate(shelf)
        resp.book_count = book_count
        return resp

    def list_shelves(self, current_user: User) -> list[ShelfResponse]:
        shelves = self.repo.list_by_user(current_user.id)
        counts = self.repo.book_counts([s.id for s in shelves])
        return [self._to_response(s, counts.get(s.id, 0)) for s in shelves]

    def create_shelf(self, name: str, current_user: User) -> ShelfResponse:
        name = name.strip()[:100]
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O nome da estante não pode ser vazio",
            )
        if self.repo.get_by_user_and_name(current_user.id, name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já tem uma estante com esse nome",
            )
        shelf = self.repo.create(
            Shelf(id=str(uuid.uuid4()), user_id=current_user.id, name=name)
        )
        return self._to_response(shelf, 0)

    def delete_shelf(self, shelf_id: str, current_user: User) -> None:
        shelf = self._owned_shelf(shelf_id, current_user)
        self.repo.delete(shelf)

    def get_shelf_detail(
        self, shelf_id: str, current_user: User
    ) -> ShelfDetailResponse:
        shelf = self._owned_shelf(shelf_id, current_user)
        books = self.repo.books_in_shelf(shelf_id)
        detail = ShelfDetailResponse.model_validate(shelf)
        detail.book_count = len(books)
        detail.books = BookService(self.db).enrich_books(books)
        return detail

    def add_book(
        self, shelf_id: str, book_id: str, current_user: User
    ) -> ShelfResponse:
        shelf = self._owned_shelf(shelf_id, current_user)
        if not self.book_repo.get_by_id(book_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )
        if self.repo.get_shelf_book(shelf_id, book_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esse livro já está nesta estante",
            )
        self.repo.add_book(ShelfBook(shelf_id=shelf_id, book_id=book_id))
        counts = self.repo.book_counts([shelf_id])
        return self._to_response(shelf, counts.get(shelf_id, 0))

    def remove_book(self, shelf_id: str, book_id: str, current_user: User) -> None:
        self._owned_shelf(shelf_id, current_user)
        shelf_book = self.repo.get_shelf_book(shelf_id, book_id)
        if not shelf_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado nesta estante",
            )
        self.repo.remove_book(shelf_book)
