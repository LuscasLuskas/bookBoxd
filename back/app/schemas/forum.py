from datetime import datetime

from pydantic import BaseModel, Field


class ForumThreadCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    book_id: str | None = None


class ForumPostCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)


class ForumPostUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)


class ForumPostResponse(BaseModel):
    id: str
    thread_id: str
    user_id: str | None
    user_name: str | None = None
    user_avatar_url: str | None = None
    body: str
    is_deleted: bool = False
    is_edited: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ForumThreadResponse(BaseModel):
    id: str
    club_id: str
    book_id: str | None
    book_title: str | None = None
    book_cover_url: str | None = None
    title: str
    is_pinned: bool
    auto_created: bool
    created_by: str | None
    created_by_name: str | None = None
    posts_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ForumThreadDetailResponse(ForumThreadResponse):
    posts: list[ForumPostResponse] = []


class ForumThreadListResponse(BaseModel):
    items: list[ForumThreadResponse]
    total: int
