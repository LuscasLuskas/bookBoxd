import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.controllers import (
    user_controller,
)
from app.middlewares.access_log_middleware import AccessLogMiddleware
from app.controllers import auth_controller, book_club_controller, book_controller, club_book_controller, membership_controller, monthly_book_controller, user_book_controller, genre_controller, tag_controller, shelf_controller, review_controller, forum_controller

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="BookBoxd API",
    description="API REST para gerenciamento de clubes de leitura",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AccessLogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# Uploaded files (profile photos) — served as static assets.
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(book_controller.router)
app.include_router(book_club_controller.router)
app.include_router(membership_controller.router)
app.include_router(club_book_controller.router)
app.include_router(monthly_book_controller.router)
app.include_router(user_book_controller.router)
app.include_router(genre_controller.router)
app.include_router(tag_controller.router)
app.include_router(shelf_controller.router)
app.include_router(review_controller.router)
app.include_router(forum_controller.router)
