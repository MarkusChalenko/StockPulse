import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI

from src.api.v1 import init_routers
from src.core.logger import LOGGING_CONFIG
from src.core.middleware import init_middlewares
from src.core.storage import create_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    """
    Asynchronous context manager for FastAPI application lifespan.

    Configures logging before the application starts.
    Args:
        app (FastAPI): The FastAPI application instance.
    Yields:
        None
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    app.redis_pool = create_redis_pool()

    yield

    await app.redis_pool.aclose()


def create_app():
    app = FastAPI(
        title="StockPulse",
        docs_url="/api/v1",
        openapi_url="/api/v1.json",
        redoc_url=None,
        lifespan=lifespan,
        version="0.0.1",
        contact={
            "name": "Mark Chalenko",
            "url": "https://t.me/MarkusChalenko",
            "email": "m.chalenko@alkor-tech.ru",
        },
        description="StockPulse"
    )

    init_middlewares(app)
    init_routers(app)

    return app
