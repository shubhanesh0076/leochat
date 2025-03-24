import redis.asyncio as redis
from utils import settings as st


class Redis:
    redis_client: redis.Redis = None

    @classmethod
    async def connect(
        cls, host: str = "localhost", port: int = 6379, username=None, password=None
    ):
        """
        Connect to Redis server.
        """

        try:
            cls.redis_client = redis.Redis(
                host=host, port=port, username=username, password=password
            )
            # await cls.redis_client.publish(channel='', message='')
        except redis.RedisError as e:
            print(f"Failed to connect to Redis: {e}")
            raise

        return cls.redis_client

    @classmethod
    async def close(cls):
        """
        close redis connection.
        """
        if cls.redis_client is not None:
            await cls.redis_client.aclose()

    @classmethod
    async def insert_val(cls, key: str, value: str, ex=900):
        """
        get insert the string into redis db
        """
        await cls.redis_client.set(key, value, ex=ex)

    @classmethod
    async def query_key(cls, key: str):
        """
        get specifig string from redis db.
        """
        try:
            value = await cls.redis_client.get(key)
            value = value.decode("utf-8")
        except Exception as e:
            return value
        return value
