from pydantic import BaseModel, Field


class CreateImage(BaseModel):
    name: str = Field(nullable=False)


class Image(CreateImage):
    id: int = Field(description="Уникальный идентификатор", nullable=False)

    class Config:
        orm_mode = True

class ImageInfo(BaseModel):
    id: int = Field(description="Уникальный идентификатор", nullable=False)

    class Config:
        orm_mode = True