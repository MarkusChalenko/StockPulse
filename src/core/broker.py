import asyncio
from contextlib import AbstractAsyncContextManager
from typing import Optional, Union

from redis.asyncio.client import PubSub
from redis.asyncio import Redis, ConnectionPool


from typing import Protocol


class Broker(Protocol, AbstractAsyncContextManager):
    """Протокол асинхронного контекстного менеджера для работы с брокером сообщений"""
    async def __aenter__(self) -> 'Broker':
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    async def publish(self, message: Union[str, bytes, dict]) -> None:
        """Публикация сообщения в канал"""
        raise NotImplementedError

    async def get_message(self, timeout: float) -> Optional[str]:
        """Получение сообщения из канала"""
        raise NotImplementedError

    async def subscribe(self, ch: str) -> None:
        """Подписка на канал"""
        raise NotImplementedError


class RedisPubSub(Broker):
    """Контекстный менеджер для работы с Redis Pub/Sub"""
    _connection: Optional[Redis]
    _pubsub: Optional[PubSub]
    _ch: Optional[str]

    def __init__(self, con: Redis):
        """
        Инициализация Broker

        Args:
            con: Существующее соединение
        """
        self._connection = con

    async def __aenter__(self) -> 'RedisPubSub':
        self._pubsub = self._connection.pubsub(ignore_subscribe_messages=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._pubsub:
            await self._pubsub.aclose()
        if self._connection:
            await self._connection.aclose()

    async def publish(self, message: Union[str, bytes, dict]) -> None:
        """Публикация сообщения в канал"""
        if not self._connection:
            raise RuntimeError("Соединение не установлено")

        if not self._ch:
            raise RuntimeError("Нет подписки на канал")

        if isinstance(message, dict):
            import json
            message = json.dumps(message)

        await self._connection.publish(self._ch, message)

    async def subscribe(self, ch: str) -> None:
        """Подписка на канал"""
        if not self._connection:
            raise RuntimeError("Соединение не установлено")

        self._ch = ch

        await self._pubsub.subscribe(self._ch)

    async def get_message(self, timeout: float = 120.0) -> Optional[str]:
        if not self._pubsub:
            raise RuntimeError("PubSub не инициализирован")

        if not self._ch:
            raise RuntimeError("Нет подписки на канал")

        try:
            message = await asyncio.wait_for(
                self._get_next_message(),
                timeout=timeout
            )
            return message
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                f"Сообщение не получено в течение {timeout} секунд"
            )

    async def _get_next_message(self) -> str:
        async for message in self._pubsub.listen():
            if message.get('type') == 'message':
                return message.get('data')
