from typing import Optional
import re

from src.core.broker import Broker


def parse_4digit_code(text: str) -> Optional[str]:
    """Возвращает 4-значный код как строку или None, если не найден."""
    RE_ANY_4 = re.compile(r'(?<!\d)(\d{4})(?!\d)')

    m = RE_ANY_4.search(text)
    if m:
        return m.group(1)
    return None


async def publish_otp_code(broker:Broker, raw_message: str) -> bool:
    async with broker as br:
        await br.subscribe("otp_code")
        await br.publish(parse_4digit_code(raw_message))

    return True
