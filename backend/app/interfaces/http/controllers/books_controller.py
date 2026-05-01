from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.db.session import get_session
from app.application.services.book_service import BookService
from app.interfaces.http.schemas.book import BookCreateRequest, BookResponse
from app.interfaces.http.middlewares.auth_middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=BookResponse)
async def create_book(request_body: BookCreateRequest, request: Request, session: AsyncSession = Depends(get_session)):
    user = get_current_user(request)
    book_service = BookService()
    try:
        book = await book_service.create_book(session, request_body.title, request_body.author, request_body.synopsis, user)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BookResponse(
        id=str(book.id),
        title=book.title,
        author=book.author,
        synopsis=book.synopsis,
        created_by=str(book.created_by) if book.created_by else None,
        created_by_name_snapshot=book.created_by_name_snapshot,
        created_at=book.created_at,
    )
