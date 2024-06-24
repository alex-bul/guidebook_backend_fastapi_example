from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from core.utils import Object
from schemas.city import City, CreateCity, CityAdmin
from schemas.category import Category, CreateCategory
from schemas.user import CreateUser

from typing import List
from core.vk_utils import get_user_id_by_link

from sqlalchemy.orm import Session
from db.methods import get_all_cities, get_all_categories, create_city as _create_city, get_user, create_user, \
    create_category as _create_category, get_category, delete_object
from db.database import get_db

from core.dependencies import verify_token, verify_user_admin

router = APIRouter(tags=['Общая информация'])


@router.get("/cities", response_model=List[City])
def get_cities(limit: int = 1000, offset: int = 0, db: Session = Depends(get_db)) -> list[City]:
    return get_all_cities(db, limit, offset)


@router.get("/cities/admin", dependencies=[Depends(verify_token), Depends(verify_user_admin)],
            response_model=List[CityAdmin], description="По сравнению с обычным методом, "
                                                        "позволяет получать дополнительную информацию о городах,"
                                                        " только для админов")
def get_cities(limit: int = 1000, offset: int = 0, db: Session = Depends(get_db)) -> list[CityAdmin]:
    return get_all_cities(db, limit, offset)


@router.get("/categories")
def get_categories(limit: int = 1000, offset: int = 0, db: Session = Depends(get_db)) -> List[Category]:
    return get_all_categories(db, limit, offset)


@router.post("/categories/create", dependencies=[Depends(verify_token), Depends(verify_user_admin)],
             response_model=Category)
def create_category(name: str, db: Session = Depends(get_db)) -> Category:
    category = _create_category(db, CreateCategory(name=name))
    return category


@router.delete("/categories/{category_id}", dependencies=[Depends(verify_token), Depends(verify_user_admin)])
def delete_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(404, "Не найдено")

    delete_object(db, category_id, Object.CATEGORY)

    from db.models import Organization

    organizations: list[Organization] = db.query(Organization).all()
    for i in organizations.copy():
        if len(i.categories) == 0:
            delete_object(db, i.id, Object.ORGANISATION)

    return {'status': 'ok'}


@router.post("/cities/create", dependencies=[Depends(verify_token), Depends(verify_user_admin)], response_model=City)
def create_city(name: str, user_link: str, db: Session = Depends(get_db)) -> City:
    user_id = get_user_id_by_link(user_link)
    user = get_user(db, user_id)
    if not user:
        create_user(db, CreateUser(id=user_id))

    city = _create_city(db, CreateCity(name=name, owner_id=user_id))
    return city
