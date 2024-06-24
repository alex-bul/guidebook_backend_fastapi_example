import logging
import random
import threading
import time

import vk_api.exceptions
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor

from core.config import settings, subscription_data, Subscriptions
from core.utils import ADMINS
from core.robokassa import generate_payment_link

vk = VkApi(token=settings.vk_group_token)


def send_message(id, text="", n=None, a=None, reply_to=None):
    return vk.method("messages.send",
                     {"peer_id": id, "message": str(text), "attachment": a, "keyboard": n, "reply_to": reply_to,
                      "random_id": random.randint(1, 2147483647)})


def send_text_to_admins(text):
    for user_id in ADMINS:
        try:
            send_message(user_id, text)
        except vk_api.VkApiError:
            pass


def send_payment_url(user_id, organisation_id, sub_type=1, description="Оплата подписки",
                     message="Оплата подписки"):
    out_sum = subscription_data[sub_type - 1][1]
    link = generate_payment_link(
        merchant_login=settings.robokassa_login,
        merchant_password_1=settings.robokassa_password,
        cost=out_sum,
        description=description,
        number=0,
        shp_user_id=user_id,
        shp_organisation_id=organisation_id,
        shp_sub_type=sub_type,
        is_test=int(settings.debug),
    )

    keyboard = VkKeyboard(inline=True)
    keyboard.add_openlink_button("Оплатить", link)

    send_message(user_id, f"{message}", n=keyboard.get_keyboard())
