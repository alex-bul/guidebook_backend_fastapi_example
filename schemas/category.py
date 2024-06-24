from pydantic import BaseModel, Field


class CreateCategory(BaseModel):
    name: str = Field(nullable=False)


class Category(CreateCategory):
    id: int = Field(description="Уникальный идентификатор", nullable=False)

    class Config:
        orm_mode = True