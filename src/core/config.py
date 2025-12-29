import multiprocessing
from functools import lru_cache
from typing import Optional, Dict

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Application settings for the StockPulse FastAPI application.

    Attributes:
        APP_PORT (int): Port on which the application runs.
        APP_HOST (str): Host address for the application.
        APP_RELOAD (bool): Enable or disable live reload.
        APP_CPU_COUNT (Optional[int]): Number of CPU workers; uses env var or auto-detection.

        REDIS_URL (str): Redis connection url
        REDIS_POOL_MAX_CONNECTIONS (int): Count of redis-pool active connections

        SELENIUM_PHONE_NUMBER (str): T-client auth phone number
        SELENIUM_MAIN_URL (str): T-client selenium entrypoint urk
    """
    APP_PORT: int = 8000
    APP_HOST: str = '0.0.0.0'
    APP_RELOAD: bool = False
    APP_CPU_COUNT: Optional[int]

    REDIS_URL: str = "redis://localhost:6379"
    REDIS_POOL_MAX_CONNECTIONS: int = 3

    SELENIUM_PHONE_NUMBER: str = "+79780353541"
    SELENIUM_MAIN_URL: str = "https://www.tbank.ru/"

    class Config:
        env_file = ".env"
        extra = 'allow'


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


# набор опций для запуска сервера
def get_server_options() -> Dict:
    app_settings = get_settings()
    return {
        "host": app_settings.APP_HOST,
        "port": app_settings.APP_PORT,
        "workers": app_settings.APP_CPU_COUNT or multiprocessing.cpu_count(),
        "reload": app_settings.APP_RELOAD
    }
