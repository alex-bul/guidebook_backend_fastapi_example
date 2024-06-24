from core.vk_auth import is_user_admin, is_user_banned, get_user_by_token as _get_user_by_token
from fastapi import FastAPI, Header, HTTPException


async def verify_token(authorization: str = Header(default='')):
    user = _get_user_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    if is_user_banned(user):
        raise HTTPException(status_code=403, detail="Вы забанены")


async def verify_user_admin(authorization: str = Header(default='')):
    user = _get_user_by_token(authorization)
    if not is_user_admin(user):
        raise HTTPException(status_code=403, detail="Вы должны быть админом")


async def get_authorization_user(authorization: str = Header(default='')):
    return _get_user_by_token(authorization)
