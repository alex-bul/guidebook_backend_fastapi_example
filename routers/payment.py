import vk_api
from fastapi import APIRouter, Depends, Request
from schemas.user import User

from core.robokassa import result_payment
from core.dependencies import verify_token, verify_user_admin
from core.validators import is_object_exists
from core.config import settings

from sqlalchemy.orm import Session
from db.methods import update_user, get_user, get_organization, pay_for_organisation
from db.database import get_db

from vk_tools import send_message, send_text_to_admins

router = APIRouter(prefix='/payment', tags=['Платежи'])


@router.post("/give", response_model=User, dependencies=[Depends(verify_token), Depends(verify_user_admin)])
def give_money_user(user_id: int, value: int, db: Session = Depends(get_db)) -> User:
    is_object_exists(db, user_id, "Пользователь не найден", get_user)
    user = get_user(db, user_id)
    update_user(db, user_id, {"rubles": user.rubles + value})
    return user


@router.get("")
def accept_payment(request: Request, db: Session = Depends(get_db)):
    result = result_payment(settings.robokassa_password_2, request.query_params.__str__())
    if result == 'bad sign':
        return result

    user_id = int(request.query_params.get('shp_user_id', 0))
    organisation_id = int(request.query_params.get('shp_organisation_id', 0))
    sub_type = int(request.query_params.get('shp_sub_type', 0))
    income = int(request.query_params.get('OutSum'))

    is_object_exists(db, user_id, "Пользователь не существует", get_user)
    is_object_exists(db, organisation_id, "Организация не существует", get_organization)

    pay_for_organisation(db, organisation_id, income, sub_type)
    organisation = get_organization(db, organisation_id)

    try:
        send_message(user_id, f'Оплата за "{organisation.name}" успешно зачислена!')
    except vk_api.VkApiError:
        pass
    send_text_to_admins(f"Новая оплата\n\n"
                        f"Название: {organisation.name}\n"
                        f"Описание: {organisation.description}\n"
                        f"Создатель: vk.com/id{organisation.owner_id}")
    return result
