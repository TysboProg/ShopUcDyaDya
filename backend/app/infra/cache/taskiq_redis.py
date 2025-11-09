from settings.config import settings
from taskiq import TaskiqScheduler
from taskiq_redis import RedisAsyncResultBackend, RedisScheduleSource, RedisStreamBroker

redis_backend = RedisAsyncResultBackend(redis_url=settings.redis.url.encoded_string())

redis_broker = RedisStreamBroker(
    url=settings.redis.url.encoded_string(),
).with_result_backend(redis_backend)

redis_source = RedisScheduleSource(
    url=settings.redis.url.encoded_string(),
)

scheduler = TaskiqScheduler(
    broker=redis_broker,
    sources=[redis_source],
)
