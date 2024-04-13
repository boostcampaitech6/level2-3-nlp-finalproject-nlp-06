import datetime
from sqlmodel import SQLModel, Field, create_engine
# from redis_om import HashModel, get_redis_connection
import redis.asyncio as aioredis
import redis

from fastapi import Request, Depends
from redis.asyncio import Redis

from config import config



async def connect_to_redis():
    redis = await aioredis.from_url(config.redis_url)
    return redis


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis






