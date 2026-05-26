from datetime import datetime

from pydantic import BaseModel, Field

from app.models.user import Role
from app.schemas.book import BookResponse


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    avatar_url: str | None = None
    bio: str | None = None
    favorite_book_id: str | None = None
    favorite_book: BookResponse | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicUserResponse(BaseModel):
    """A user as seen by someone visiting their profile — never exposes email."""

    id: str
    name: str
    role: Role
    avatar_url: str | None = None
    bio: str | None = None
    favorite_book_id: str | None = None
    favorite_book: BookResponse | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    bio: str | None = Field(None, max_length=2000)
    favorite_book_id: str | None = None


class UserDeleteResponse(BaseModel):
    message: str
