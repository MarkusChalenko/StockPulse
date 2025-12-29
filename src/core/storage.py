import logging
from contextlib import AbstractAsyncContextManager
from typing import Optional, Any, Protocol

from redis import RedisError
from redis.asyncio import ConnectionPool, Redis

from src.core.config import get_settings

logger = logging.getLogger("storage")


def create_redis_pool() -> ConnectionPool:
    return ConnectionPool().from_url(
        url=get_settings().REDIS_URL,
        decode_responses=True,
        encoding="utf-8",
        db=0,
        max_connections=get_settings().REDIS_POOL_MAX_CONNECTIONS
    )


class Storage(Protocol, AbstractAsyncContextManager):
    async def __aenter__(self) -> 'Storage':
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Установка ключ-значение"""
        raise NotImplementedError

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        raise NotImplementedError

    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        raise NotImplementedError

    # Делегирование методов к клиенту
    def __getattr__(self, name: str):
        """Делегирование методов к клиенту"""
        raise NotImplementedError


class RedisStorage(Storage):
    """Контекстный менеджер для работы с Redis"""

    def __init__(self, con: Redis):
        """
        Инициализация Store

        Args:
            con: Существующее соединение
        """
        self._redis: Redis = con

    async def __aenter__(self) -> 'RedisStorage':
        """Вход в контекстный менеджер"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера"""
        if self._redis:
            await self._redis.close()

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Установка ключ-значение"""
        if not self._redis:
            raise RuntimeError("Store must be used within async with context")

        try:
            if ttl:
                await self._redis.setex(key, ttl, value)
            else:
                await self._redis.set(key, value)
            return True
        except RedisError as e:
            logger.error(f"Failed to set key {key}: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Получение значения по ключу"""
        if not self._redis:
            raise RuntimeError("Store must be used within async with context")

        try:
            return await self._redis.get(key)
        except RedisError as e:
            logger.error(f"Failed to get key {key}: {e}")
            raise

    async def delete(self, key: str) -> bool:
        """Удаление ключа"""
        if not self._redis:
            raise RuntimeError("Store must be used within async with context")

        try:
            result = await self._redis.delete(key)
            return bool(result)
        except RedisError as e:
            logger.error(f"Failed to delete key {key}: {e}")
            raise

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if not self._redis:
            raise RuntimeError("Store must be used within async with context")

        try:
            result = await self._redis.exists(key)
            return bool(result)
        except RedisError as e:
            logger.error(f"Failed to check key {key}: {e}")
            raise

    # Делегирование методов к Redis клиенту
    def __getattr__(self, name: str):
        """Делегирование методов к Redis клиенту"""
        if not self._redis:
            raise RuntimeError("Store must be used within async with context")

        if hasattr(self._redis, name):
            return getattr(self._redis, name)
        raise AttributeError(f"'Store' object has no attribute '{name}'")
