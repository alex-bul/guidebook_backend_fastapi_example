from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from fastapi.exceptions import StarletteHTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every

from ratelimit import RateLimitMiddleware, Rule
from ratelimit.auths.ip import client_ip
from ratelimit.backends.simple import MemoryBackend

from db.database import create_all_models

from core.cron import wait_midnight_and_do_actions, wait_month_start_and_do_actions
from core.config import settings
from excel_parser import upload_data_from_source, admins_and_city_create

from routers import images, users, other, organizations, payment

import uvicorn
import threading

app = FastAPI(debug=settings.debug, title="Справочник услуг и заведений",
              description="Сервис, реализующий REST API для веб-приложения на платформе VK Mini Apps"
                          " с каталогом услуг и заведений в городе. Реализована часть для пользователей "
                          "и методы для администратора, позволяющие управлять приложением через интерфейс.\n\n"
                          "Для локального тестирования используйте super-user токен для авторизации: "
                          "dG6Soif%K0odbM2w27zC2Lzoq#1USOl9mkVssg#&jRk!kOWJp^")
app.add_middleware(
    RateLimitMiddleware,
    backend=MemoryBackend(),
    authenticate=client_ip,
    config={
        r"^/user": [Rule(second=5, block_time=60)],
    },
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse({"error_code": exc.status_code, "error_message": str(exc.detail)}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"error_code": 400, "error_message": "Ошибка валидации: " + str(exc)}, status_code=400)


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24 - 60)
def make_everyday_actions() -> None:
    wait_midnight_and_do_actions()


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24 * 27 - 60)
def make_everyday_actions() -> None:
    wait_month_start_and_do_actions()


@app.on_event("startup")
def load_data() -> None:
    admins_and_city_create()
    if settings.load_file_data_on_start:
        print("Загружаю данные...")
        upload_data_from_source()


# @app.on_event("startup")
# def vk_bot():
#     print("Запустил бота")
#     worker()


# create_all_models()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images.router)
app.include_router(users.router)
app.include_router(other.router)
app.include_router(organizations.router)
app.include_router(payment.router)

if __name__ == '__main__':
    upload_data_from_source()
    create_all_models()

    # запуск приложения с помощью uvicorn
    uvicorn.run('main:app', port=8000, host='127.0.0.1', reload=True)
