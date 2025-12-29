import logging
import time
from uuid import uuid4

from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.core.logger import request_id_ctx_var, request_path_ctx_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4())[:8])
        request_id_ctx_var.set(request_id)
        request_path_ctx_var.set(request.url.path)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger()
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Request failed: {exc}", exc_info=True)
            raise
        finally:
            execution_time = time.time() - start_time
            logger.info(f"Request processed in {execution_time:.3f}s")

        return response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger = logging.getLogger()
            logger.error(f"Unhandled exception: {exc}", exc_info=True)

            from starlette.responses import JSONResponse
            from starlette import status

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "errorText": str(exc),
                    "hasError": True,
                    "resp": None
                }
            )


def init_middlewares(app: FastAPI):
    """Initialize all middleware."""
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ExceptionHandlingMiddleware)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )