import multiprocessing
from typing import Optional

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Application settings for the StockPulse FastAPI application.

    Attributes:
        app_port (int): Port on which the application runs.
        app_host (str): Host address for the application.
        app_reload (bool): Enable or disable live reload.
        app_cpu_count (Optional[int]): Number of CPU workers; uses env var or auto-detection.
    """
    app_port: int = 8000
    app_host: str = '0.0.0.0'
    app_reload: bool = False
    app_cpu_count: Optional[int]

    class Config:
        env_file = ".env"
        extra = 'allow'


app_settings = AppSettings()

# набор опций для запуска сервера
uvicorn_options = {
    "host": app_settings.app_host,
    "port": app_settings.app_port,
    "workers": app_settings.app_cpu_count or multiprocessing.cpu_count(),
    "reload": app_settings.app_reload
}
