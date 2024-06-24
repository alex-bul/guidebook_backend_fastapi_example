from pydantic import BaseModel, Field

from typing import Optional


class CreateCity(BaseModel):
    name: str = Field(nullable=False)
    owner_id: Optional[int]


class CityInfo(BaseModel):
    id: int = Field(description="Уникальный идентификатор", nullable=False)
    name: str = Field(nullable=False)

    class Config:
        orm_mode = True


class City(CreateCity):
    id: int = Field(description="Уникальный идентификатор", nullable=False)

    organizationCount: Optional[int]

    class Config:
        orm_mode = True


class CityAdmin(City):
    income: int
    incomeMonth: int
    owner_id: Optional[int]
