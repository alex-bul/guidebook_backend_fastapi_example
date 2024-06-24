import random
import time
import re

import vk_api.exceptions
from fastapi.exceptions import HTTPException

from vk_api import VkApi, ApiError
from core.config import settings

ACCESS_TOKEN = settings.app_secure_key
user_cache = {}


def api_user_data(user_ids: str):
    c = 3
    vk = VkApi(token=ACCESS_TOKEN)
    while c:
        c -= 1
        try:
            return vk.method("users.get", {"user_ids": user_ids, "fields": "photo_100", "lang": "ru"})
        except ApiError as ex:
            time.sleep(random.randint(1, 5) * 0.33)


def get_users_vk(ids=None) -> dict:
    if ids is None:
        ids = []
    user_ids = str()

    result_cache = []
    result = []
    for i in ids:
        cache_user = get_from_cache(int(i))
        if cache_user:
            result_cache.append(cache_user)
        else:
            user_ids += str(i) + ","
    if user_ids:
        result = api_user_data(user_ids)
    write_cache(result)
    result += result_cache

    return result


def get_from_cache(user_id):
    if user_id in user_cache:
        if time.time() - user_cache[user_id]['time_update'] < 48 * 60 * 60:
            return user_cache[user_id]


def write_cache(user_list):
    for us in user_list:
        us['time_update'] = time.time()
        user_cache[us['id']] = us


def get_user_name_and_photo(user_id):
    return get_users_vk([user_id])[0]


def get_user_id_by_link(link):
    regex = r"((http|https):\/\/)?(m\.)?vk.(ru|com)\/([a-z\._0-9]*)"
    match = re.match(regex, link)
    if not match:
        raise HTTPException(400, "Невалидная ссылка")

    screen_name = match.group(5)
    vk = VkApi(token=ACCESS_TOKEN)
    try:
        result = vk.method("utils.resolveScreenName", {"screen_name": screen_name})
        if result['type'] != "user":
            raise HTTPException(400, "Ссылка должна вести на страницу пользователя")
        return result['object_id']
    except vk_api.exceptions.VkApiError:
        raise HTTPException(422, "Ошибка при расшифровке ссылки")



