import logging

from fastapi import APIRouter

from src.api.v1.dependencies import BrokerDep
from src.service.code_service import publish_otp_code

router = APIRouter()

logger = logging.getLogger("message")


@router.get("/send")
async def send_code(s: str, br: BrokerDep):
    await publish_otp_code(br, s)

    return {"status": "ok"}
