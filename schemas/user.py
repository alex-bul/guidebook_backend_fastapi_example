from enum import Enum
from pydantic import BaseModel, Field

from schemas.city import CityInfo
from schemas.organization import Organization
from typing import List, Optional


class UserRoles(Enum):
    BANNED = -1
    COMMON = 0
    ADMIN = 10


class CreateUser(BaseModel):
    id: int = Field(description="Уникальный идентификатор", nullable=False)
    role: UserRoles = Field(default=UserRoles.COMMON, nullable=False)


class UserInfo(CreateUser):
    rubles: int = 0

    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]

    city: Optional[CityInfo]

    class Config:
        orm_mode = True


class User(UserInfo):
    organizations: Optional[List[Organization]]

    class Config:
        orm_mode = True
