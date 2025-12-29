from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from starlette.requests import Request

from src.core.broker import RedisPubSub, Broker
from src.core.storage import Storage, RedisStorage


async def get_storage(request: Request):
    return RedisStorage(Redis(connection_pool=request.app.redis_pool))

StorageDep = Annotated[Storage, Depends(get_storage)]


async def get_broker(request: Request) -> Broker:
    return RedisPubSub(Redis(connection_pool=request.app.redis_pool, decode_responses=True))

BrokerDep = Annotated[Broker, Depends(get_broker)]
