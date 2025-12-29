from fastapi import FastAPI

from . import otp, internal


def init_routers(app: FastAPI):
    """Initialize all routers."""
    app.include_router(otp.router, prefix="/message", tags=['message'])
    app.include_router(internal.router, tags=['internal'])


