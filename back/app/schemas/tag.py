from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    id: str
    name: str
    # The user who applied this tag to the book (null once that account is gone).
    added_by: str | None = None

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    items: list[TagResponse]
