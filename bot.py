import logging
import random
import os

import time

import vk_api.exceptions
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy_utils import database_exists, create_database

from db.models import Organization, User

from core.utils import ADMINS
from core.config import settings

VK_GROUP_TOKEN = settings.vk_group_token
SQLALCHEMY_DATABASE_URL = settings.db_url()

vk = VkApi(token=VK_GROUP_TOKEN)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c timezone=utc"},
    pool_size=100, max_overflow=10
)

if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def send_message(id, text="", n=None, a=None, reply_to=None):
    return vk.method("messages.send",
                     {"peer_id": id, "message": str(text), "attachment": a, "keyboard": n, "reply_to": reply_to,
                      "random_id": random.randint(1, 2147483647)})


def bot():
    print("Бот запущен")
    current_choice = {}

    def keyboard_main():
        keyboard = VkKeyboard(one_time=False, inline=False)
        keyboard.add_button("Рассылка пользователям")
        keyboard.add_line()
        keyboard.add_button("Рассылка владельцам организаций")
        return keyboard.get_keyboard()

    def keyboard_cancel():
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def keyboard_start_cancel():
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_button("Старт", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def send_to_users(audience, text, initial_user_id):
        db: Session = SessionLocal()

        if audience == "owners":
            users = list(
                set([i[0] for i in db.query(Organization.owner_id).filter(Organization.owner_id != None).all()]))
        else:
            users = [i[0] for i in db.query(User.id).all()]

        send_message(initial_user_id, f"В очереди на рассылку {len(users)} пользователей")
        while users:
            current = ",".join([str(i) for i in users[:100]])
            users = users[100:]
            vk.method("messages.send",
                      {"peer_ids": current, "message": text,
                       "random_id": random.randint(1, 2147483647)})
        try:
            send_message(initial_user_id, "Рассылка завершена!")
        except:
            pass

    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.to_me and event.type == VkEventType.MESSAGE_NEW:
            user_id = event.user_id
            body = event.text

            if user_id in ADMINS:
                if body == "Рассылка пользователям":
                    current_choice[user_id] = "users"
                    send_message(user_id, "Пришлите текст для рассылки", keyboard_cancel())
                elif body == "Рассылка владельцам организаций":
                    current_choice[user_id] = "owners"
                    send_message(user_id, "Пришлите текст для рассылки", keyboard_cancel())
                elif body == "Отмена":
                    if user_id in current_choice:
                        del current_choice[user_id]
                    send_message(user_id, "Отменено")
                elif body == "Старт" and current_choice.get(user_id, None):
                    send_message(user_id, "Начал рассылку!")
                    send_to_users(*current_choice[user_id], user_id)
                elif isinstance(current_choice.get(user_id, None), str):
                    text = f"Аудитория рассылки: " + \
                           ("владельцы организаций" if current_choice[user_id] == "owners" else "пользователи") + '\n'
                    text += f"Текст рассылки:\n\n{body}"
                    send_message(user_id, text, keyboard_start_cancel())
                    current_choice[user_id] = [current_choice[user_id], body]
                else:
                    send_message(user_id, "Пользуйся командами!", keyboard_main())


def worker():
    while True:
        try:
            bot()
        except vk_api.exceptions.VkApiError as ex:
            if not VK_GROUP_TOKEN:
                print("Токен не задан, бот не будет работать")
                time.sleep(60 * 60 * 3)
            print("Ошибка бота", str(ex))
            logging.exception(ex)
            time.sleep(3)


if __name__ == '__main__':
    worker()
