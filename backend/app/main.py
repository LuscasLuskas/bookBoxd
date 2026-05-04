import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.logging.logger import configure_logging
from app.infrastructure.db.session import init_db
from app.interfaces.http.middlewares.auth_middleware import AuthMiddleware
from app.interfaces.http.controllers.auth_controller import router as auth_router
from app.interfaces.http.controllers.books_controller import router as books_router
from app.interfaces.http.controllers.clubs_controller import router as clubs_router
from app.interfaces.http.controllers.memberships_controller import router as memberships_router
from app.interfaces.http.controllers.users_controller import router as users_router
from app.interfaces.http.controllers.health_controller import router as health_router

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    pass

app = FastAPI(
    title="BookBoxd Backend",
    description="Backend API for BookBoxd, a book club management application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(books_router, prefix="/books", tags=["books"])
app.include_router(clubs_router, prefix="/clubs", tags=["clubs"])
app.include_router(memberships_router, prefix="/memberships", tags=["memberships"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(health_router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to BookBoxd API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }
