from fastapi import APIRouter, Depends
from schemas.user import User, UserInfo, UserRoles
from schemas.city import City, CityAdmin
from schemas.organization import Organization

from typing import List
from core.dependencies import get_authorization_user, verify_token, verify_user_admin
from sqlalchemy.orm import Session

from db.database import get_db
from db.methods import update_user, get_user

from core.vk_utils import get_user_name_and_photo
from core.validators import is_object_exists

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get("/me", dependencies=[Depends(verify_token)], response_model=UserInfo)
def get_me(user: User = Depends(get_authorization_user), db: Session = Depends(get_db)):
    user = get_user(db, user.id)

    user_info = UserInfo.from_orm(user)
    vk_data = get_user_name_and_photo(user_info.id)

    user_info.first_name = vk_data['first_name']
    user_info.last_name = vk_data['last_name']
    user_info.avatar = vk_data['photo_100']

    return user_info


@router.get("/me/organizations", dependencies=[Depends(verify_token)], response_model=List[Organization])
def get_my_organizations(db: Session = Depends(get_db), user: User = Depends(get_authorization_user)):
    user = get_user(db, user.id)
    return user.organizations


@router.post("/set_city", dependencies=[Depends(verify_token)], response_model=UserInfo)
def set_city_current_user(city_id: int, user: User = Depends(get_authorization_user),
                          db: Session = Depends(get_db)) -> UserInfo:
    r = update_user(db, user.id, {"city_id": city_id})
    return r


@router.post("/set_role", dependencies=[Depends(verify_token), Depends(verify_user_admin)], response_model=UserInfo)
def set_city_current_user(user_id: int, role: int,
                          db: Session = Depends(get_db)) -> UserInfo:
    is_object_exists(db, user_id, "Пользователь не найден", get_user)

    new_role = UserRoles.COMMON
    if role == 10:
        new_role = UserRoles.ADMIN
    elif role == -1:
        new_role = UserRoles.BANNED

    return update_user(db, user_id, {"role": new_role})


@router.get("/me/cities", dependencies=[Depends(verify_token)], response_model=List[CityAdmin])
def get_my_cities(db: Session = Depends(get_db), user: User = Depends(get_authorization_user)):
    user = get_user(db, user.id)
    result = []
    for city in user.cities:
        organization_count = len(city.organizations)
        city_obj: City = City.from_orm(city)
        city_obj.organizationCount = organization_count
        result.append(result)
    return user.cities
