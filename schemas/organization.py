import datetime

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.city import City
from schemas.image import ImageInfo
from schemas.category import Category


class OrganizationInfo(BaseModel):
    name: str

    images: List[ImageInfo]

    site: Optional[str]
    description: Optional[str]
    email: Optional[str]
    phone: Optional[str]

    address: str
    workingDay: str

    owner_id: Optional[int]


class CreateOrganization(OrganizationInfo):
    images: List[int]

    categories: List[int]
    city_id: int

    owner_id: int


class UpdateOrganization(OrganizationInfo):
    id: int = Field(description="Уникальный идентификатор",
                    nullable=False)
    images: List[ImageInfo]

    categories: List[Category]
    city: City

    owner_id: int


class Organization(OrganizationInfo):
    id: int = Field(description="Уникальный идентификатор",
                    nullable=False)
    description: Optional[str] = Field(description="Описание",
                                       nullable=True)

    paidFor: bool
    hidden: bool

    statAll: int
    statDay: int

    categories: List[Category]
    city: City

    class Config:
        orm_mode = True
