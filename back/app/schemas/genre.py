from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class GenreListResponse(BaseModel):
    items: list[GenreResponse]
