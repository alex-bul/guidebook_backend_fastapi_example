import datetime
import enum

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url_from_env: str = Field(default="", env='POSTGRES_URL_ENV')
    db_url_from_docker: str = Field(default=None, env='POSTGRES_URL_DOCKER')

    load_file_data_on_start: bool = Field(default=False, env='LOAD_FILE_DATA_ON_START')

    client_secret: str = Field(default="", env='CLIENT_SECRET')
    app_secure_key: str = Field(default="", env='APP_SECURE_KEY')
    superuser_token: str = Field(default="dG6Soif%K0odbM2w27zC2Lzoq#1USOl9mkVssg#&jRk!kOWJp^", env='SUPERUSER_TOKEN')
    vk_group_token: str = Field(default="", env='VK_GROUP_TOKEN')

    robokassa_login: str = Field(default="", env='ROBOKASSA_LOGIN')
    robokassa_password: str = Field(default="", env='ROBOKASSA_PASSWORD')
    robokassa_password_2: str = Field(default="", env='ROBOKASSA_PASSWORD_2')

    debug: bool = Field(default=True, env='DEBUG')

    PLACE_VISIT_TIMEOUT: int = 60 * 60 * 5

    def db_url(self):
        if self.db_url_from_docker:
            return self.db_url_from_docker
        return self.db_url_from_env

    class Config:
        env_file = ".env"


class Subscriptions:
    MONTH = 1
    HALF_YEAR = 2
    YEAR = 3


subscription_data = [
    ("Подписка на месяц", 59),
    ("Подписка на полгода", 294),
    ("Подписка на год", 468)
]


def get_subscription_offset(sub_type):
    if sub_type == Subscriptions.MONTH:
        return datetime.timedelta(days=30)
    elif sub_type == Subscriptions.HALF_YEAR:
        return datetime.timedelta(days=180)
    elif sub_type == Subscriptions.YEAR:
        return datetime.timedelta(days=365)


settings = Settings()
