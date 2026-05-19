from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    created_at: datetime

    model_config = {"from_attributes": True}


class UserDeleteResponse(BaseModel):
    message: str
