from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlparse, parse_qsl, urlencode

from typing import Optional

from fastapi import Request
from fastapi.exceptions import HTTPException

from core.config import settings
from db.methods import create_user, get_user
from db.database import SessionLocal
from db.models import User
from schemas.user import CreateUser, UserRoles


def get_user_by_token(token) -> Optional[User]:
    user_id = get_user_id_by_token(token)
    if not user_id:
        return None

    db = SessionLocal()
    user = get_user(db, user_id)
    if not user:
        user = create_user(db, CreateUser(id=user_id))
    db.close()
    return user


def is_user_admin(user: User):
    return getattr(user, "role", None) == UserRoles.ADMIN


def is_user_banned(user: User):
    return getattr(user, "role", None) == UserRoles.BANNED


def get_user_id_by_token(token):
    query = token

    if not query:
        return None
    if query == settings.superuser_token:
        return 242306128

    query_params = dict(parse_qsl(query, keep_blank_values=True))
    status = is_valid(query=query_params, secret=settings.client_secret)
    return int(query_params.get('vk_user_id')) if status else None


def is_valid(*, query: dict, secret: str) -> bool:
    """Check VK Apps signature"""
    vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    hash_code = b64encode(HMAC(secret.encode(), urlencode(vk_subset, doseq=True).encode(), sha256).digest())
    decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    return query.get('sign', None) == decoded_hash_code
