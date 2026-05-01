from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None = None
    role: str
    created_at: datetime


class DeleteUserResponse(BaseModel):
    success: bool
