import logging

import requests
from fastapi import APIRouter

from src.api.v1.dependencies import StorageDep
from src.selenium_script import get_cookies_from_t

router = APIRouter()
logger = logging.getLogger("internal")


@router.get("/ping")
async def health_check() -> str:
    """Health check endpoint."""
    logger.info("Health check requested")
    return "pong"


@router.get("/test")
async def root():
    cookies = await get_cookies_from_t()
    s = requests.Session()

    s.cookies.set('navi_token', cookies.navi_token)
    s.cookies.set('gwSessionID', cookies.gwSessionID)

    resp = s.get(f"https://www.tbank.ru/api/invest-gw/social/v1/mute/profile?limit=30&sessionId={cookies.psid}")
    return resp.json()


@router.get("/r")
async def redis_test(st: StorageDep):
    async with st:
        await st.set("test", 1234)

        return await st.get("test")
