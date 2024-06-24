import datetime
import typing

from pydantic import BaseModel as BaseSchema
from db.database import Base as BaseModel

from schemas.organization import Organization as OrganizationSchema, \
    CreateOrganization as CreateOrganizationSchema
from schemas.category import CreateCategory as CreateCategorySchema, Category as CategorySchema
from schemas.user import CreateUser as CreateUserSchema, User as UserSchema
from schemas.city import CreateCity as CreateCitySchema
from schemas.image import CreateImage as CreateImageSchema, Image as ImageSchema

from db.models import Category, Image, Organization, User, City

from sqlalchemy.orm import Session
from core.utils import Object as ObjectEnum
from core.config import get_subscription_offset


def create_organization(db: Session, data: CreateOrganizationSchema):
    return creator(db, data, Organization)


def create_category(db: Session, data: CreateCategorySchema):
    return creator(db, data, Category)


def create_city(db: Session, data: CreateCitySchema):
    return creator(db, data, City)


def create_user(db: Session, data: CreateUserSchema):
    return creator(db, data, User)


def create_image(db: Session, data: CreateImageSchema):
    return creator(db, data, Image)


def creator(db: Session, data: BaseSchema, model: BaseModel):
    db_unit = model(**data.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)

    return db_unit


def get_organization(db: Session, id: int) -> Organization:
    return db.query(Organization).filter(Organization.id == id).first()


def get_user(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()


def get_category(db: Session, id: int):
    return db.query(Category).filter(Category.id == id).first()


def get_city(db: Session, id: int):
    return db.query(City).filter(City.id == id).first()


def get_image(db: Session, id: int):
    return db.query(Image).filter(Image.id == id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def update_organization(db: Session, organization_id: int, update_dict: dict):
    return updater(db, organization_id, update_dict, get_organization)


def update_user(db: Session, user_id: int, update_dict: dict):
    return updater(db, user_id, update_dict, get_user)


def update_category(db: Session, category_id: int, update_dict: dict):
    return updater(db, category_id, update_dict, get_category)


def updater(db: Session, object_id: int, update_dict: dict, get_function: typing.Callable):
    obj = get_function(db, object_id)
    for key, val in update_dict.items():
        setattr(obj, key, val)
    db.merge(obj)
    db.commit()
    return obj


def get_all_cities(db: Session, limit: int = 1000, offset: int = 0) -> typing.List[City]:
    result = db.query(City).offset(offset).limit(limit).all()
    return result


def get_all_organizations(db: Session, limit: int = 1000, offset: int = 0, is_hidden: bool = False,
                          category_filter: int = 0, city_filter: int = 0) -> typing.List[Organization]:
    result = db.query(Organization).filter(Organization.hidden == is_hidden)

    if category_filter:
        result = db.query(Category).filter(Category.id == category_filter).first()
        organization_list = list(filter(lambda x: x.hidden == is_hidden, result.organizations))
        if city_filter:
            organization_list = list(
                filter(lambda x: x.city_id == city_filter, organization_list))
        return organization_list[offset: offset + limit]

    if city_filter:
        result = result.filter(Organization.city_id == city_filter)

    return result.offset(offset).limit(limit).all()


def get_all_categories(db: Session, limit: int = 1000, offset: int = 0) -> typing.List[Category]:
    result = db.query(Category.id, Category.name).offset(offset).limit(limit).all()
    return result


def pay_for_organisation(db: Session, organisation_id: int, income: int, sub_type: int):
    organisation = get_organization(db, organisation_id)

    if organisation.next_pay_time and organisation.next_pay_time >= datetime.datetime.now():
        pay_offset = organisation.next_pay_time
    else:
        pay_offset = datetime.datetime.now()

    next_pay_time = pay_offset + get_subscription_offset(sub_type)
    organisation.last_pay_time = next_pay_time
    organisation.hidden = False

    city: City = organisation.city
    city.income += income
    city.incomeMonth += income

    owner: User = city.owner
    if owner:
        owner.rubles += income * 0.5

    db.commit()


# def get_all_places(db: Session, limit: int = 1000, offset: int = 0, show_hidden: bool = False):
#     q = db.query(Place)
#     if not show_hidden:
#         q = q.filter(Place.hidden == False)
#     return q.offset(offset).limit(limit).all()
#
#
# def get_all_tags(db: Session, limit: int = 1000, offset: int = 0):
#     return db.query(Tag).order_by(Tag.id.asc()).join(Tag.places).group_by(Tag).having(func.count(Tag.id) > 0) \
#         .offset(offset).limit(
#         limit).all()
#
#
# def get_all_posts(db: Session, limit: int = 1000, offset: int = 0, show_hidden: bool = False):
#     q = db.query(Post)
#     if not show_hidden:
#         q = q.filter(Post.hidden == False)
#     return q.order_by(Post.weight.desc(), Post.time_created.desc()).offset(offset).limit(limit).all()
#
#
# def get_all_categories(db: Session, limit: int = 1000, offset: int = 0):
#     category_list = db.query(Category.id, Category.name).offset(offset).limit(limit).all()
#     return category_list
#
#
# def get_category_posts(db: Session, category_id: int, limit: int = 1000, offset: int = 0, show_hidden: bool = False):
#     category = get_category(db, category_id)
#
#     if not category:
#         raise Exception("Категория не найдена")
#
#     q = category.posts
#     if not show_hidden:
#         q = q.filter(Post.hidden == False)
#     return q.order_by(Post.time_created.desc(), Post.weight.desc()).offset(offset).limit(limit)


def delete_object(db: Session, object_id: int, object_type: ObjectEnum) -> bool:
    if object_type == ObjectEnum.ORGANISATION:
        obj: Organization = get_organization(db, object_id)
        if not obj:
            raise Exception("Организация не найдена")
        obj.images.clear()
        obj.categories.clear()
        db.delete(obj)
    if object_type == ObjectEnum.CATEGORY:
        obj: Category = get_category(db, object_id)
        if not obj:
            raise Exception("Категория не найдена")
        obj.organizations.clear()
        db.delete(obj)
    # elif object_type == ObjectEnum.POST_CATEGORY:
    #     obj = get_category(db, object_id)
    #     if not obj:
    #         raise Exception("Категория не найдена")
    #     db.delete(obj)
    # elif object_type == ObjectEnum.POST:
    #     obj = get_post(db, object_id)
    #     if not obj:
    #         raise Exception("Пост не найден")
    #     db.delete(obj)
    db.commit()
    return True
