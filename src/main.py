import logging
import logging.config
import time
from contextlib import asynccontextmanager
from typing import AsyncContextManager
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse

from core.config import uvicorn_options
from core.logger import LOGGING_CONFIG, request_id_ctx_var, request_path_ctx_var


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    logging.config.dictConfig(LOGGING_CONFIG)
    yield


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

logger = logging.getLogger('main')


@app.middleware("http")
async def log_errors_and_execution_time(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4())[:8])
    request_id_ctx_var.set(request_id)

    request_path_ctx_var.set(request.url.path)

    request.state.start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as msg:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "errorText": str(msg),
                "hasError": True,
                "resp": None
            }
        )
    finally:
        logger.info(f"exc_time: {(time.time() - request.state.start_time):.3f} s")

    response.headers["X-Request-ID"] = request_id

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/ping")
async def root() -> str:
    logger.info("Pong!")
    return "pong"


if __name__ == '__main__':
    print(uvicorn_options)
    uvicorn.run(
        'main:app',
        **uvicorn_options
    )
