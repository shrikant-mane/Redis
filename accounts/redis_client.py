import redis
from django.conf import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

"""
Selects Database 0. Redis has 16 isolated database slots by
default (indexed 0 to 15), and 0 is the default logical database.
"""

"""
redis_client.set(...)
redis_client.get(...)
redis_client.delete(...)
redis_client.exists(...)
"""




