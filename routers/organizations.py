from typing import List

import vk_api
from fastapi import APIRouter, Depends, HTTPException

from schemas.organization import Organization, UpdateOrganization, CreateOrganization
from schemas.user import User

from sqlalchemy.orm import Session
from db.methods import get_all_organizations, get_organization, get_city, get_category, delete_object, \
    update_organization, create_organization as _create_organization, get_user, get_image
from db.database import get_db

from core.utils import Object
from core.dependencies import verify_token, get_authorization_user, is_user_admin
from core.validators import is_object_exists

from vk_tools import send_payment_url

router = APIRouter(prefix='/organizations', tags=['Организации'])


@router.get("", response_model=List[Organization])
def get_organizations(limit: int = 1000, offset: int = 0, filter: int = 0, city: int = 0, is_hidden: bool = False,
                      db: Session = Depends(get_db), user: User = Depends(get_authorization_user)):
    if city:
        is_object_exists(db, city, "Город не найден", get_city)
    else:
        if user.city_id:
            city = user.city_id

    if filter:
        is_object_exists(db, filter, "Категория не найдена", get_category)

    if is_hidden and not is_user_admin(user):
        raise HTTPException(403, "Доступ запрещен")

    return get_all_organizations(db, limit, offset, category_filter=filter, city_filter=city)


@router.get("/{organization_id}", response_model=Organization)
def get_organization_by_id(organization_id, db: Session = Depends(get_db)):
    organization = get_organization(db, organization_id)
    if not organization:
        raise HTTPException(404, "Не найдено")
    update_organization(db, organization_id, {"statDay": organization.statDay + 1, "statAll": organization.statAll + 1})
    return organization


@router.delete("/{organization_id}", dependencies=[Depends(verify_token)])
def delete_organization_by_id(organization_id, db: Session = Depends(get_db),
                              user: User = Depends(get_authorization_user)):
    organization = get_organization(db, organization_id)
    if not organization:
        raise HTTPException(404, "Не найдено")
    if organization.owner_id != user.id and not is_user_admin(user):
        raise HTTPException(403, "Доступ запрещен")
    delete_object(db, organization_id, Object.ORGANISATION)
    return {'status': 'ok'}


@router.post("", response_model=Organization, dependencies=[Depends(verify_token)])
def create_organization(data: CreateOrganization, db: Session = Depends(get_db),
                        user: User = Depends(get_authorization_user)):
    is_object_exists(db, data.owner_id, "Пользователь не найден", get_user)
    is_object_exists(db, data.city_id, "Город не найден", get_city)

    categories = data.categories.copy()
    data.categories = []
    for category_id in categories:
        is_object_exists(db, category_id, "Категория не найдена", get_category)

    images = data.images.copy()
    data.images = []
    for img_id in images:
        is_object_exists(db, img_id, "Фото не найдено", get_image)

    organization = _create_organization(db, data)

    for category_id in categories:
        organization.categories.append(get_category(db, category_id))

    for img_id in images:
        organization.images.append(get_image(db, img_id))

    if is_user_admin(user):
        organization.hidden = False
    else:
        try:
            send_payment_url(user_id=organization.owner_id, organisation_id=organization.id,
                             message=f'Оплатите подписку для «{organization.name}»', sub_type=3)
        except vk_api.VkApiError:
            raise HTTPException(400, "Разрешите сообщения от имени группы")
    db.commit()
    return organization


@router.put("", response_model=Organization, dependencies=[Depends(verify_token)])
def update_organization_data(data: UpdateOrganization, db: Session = Depends(get_db),
                        user: User = Depends(get_authorization_user)):
    if user.id != data.owner_id and not is_user_admin(user):
        raise HTTPException(400, "Вы не можете редактировать эту организацию")

    is_object_exists(db, data.owner_id, "Пользователь не найден", get_user)
    is_object_exists(db, data.city.id, "Город не найден", get_city)
    is_object_exists(db, data.id, "Организация не найдена", get_organization)

    organization = get_organization(db, data.id)
    for key in UpdateOrganization.__dict__['__fields__'].keys():
        if key == 'images':
            organization.images = []
            for i in getattr(data, key):
                image_id = i.id
                is_object_exists(db, image_id, "Фото не найдено", get_image)
                organization.images.append(get_image(db, image_id))
        elif key == 'categories':
            organization.categories = []
            for i in getattr(data, key):
                category_id = i.id
                is_object_exists(db, category_id, "Категория не найдена", get_category)
                organization.categories.append(get_category(db, category_id))
        elif key == 'city':
            organization.city = get_city(db, data.city.id)
        else:
            setattr(organization, key, getattr(data, key))

    db.commit()
    return organization
