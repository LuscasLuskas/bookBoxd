from datetime import datetime

from pydantic import BaseModel, Field


class ReviewUpsert(BaseModel):
    """Create or update the caller's review for a book."""

    book_id: str
    rating: float
    body: str | None = Field(None, max_length=5000)
    is_public: bool = True


class ReviewResponse(BaseModel):
    id: str
    user_id: str | None = None  # blanked when the review is soft-deleted
    user_name: str | None = None
    user_avatar_url: str | None = None
    book_id: str
    # Only populated when listing a user's reviews (so the profile can show
    # which book each review is about). Null on book-page review lists.
    book_title: str | None = None
    book_cover_url: str | None = None
    rating: float | None = None  # blanked when the review is soft-deleted
    body: str | None
    is_public: bool
    is_deleted: bool = False
    is_edited: bool = False
    likes_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int


class ReviewLikeResponse(BaseModel):
    review_id: str
    liked: bool
    likes_count: int
