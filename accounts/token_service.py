from datetime import datetime, timezone

from accounts.redis_client import redis_client
from django.conf import settings


#=================
# Redis Activity
#=================


def store_token(jit, user_id, expiration):
    """
    store active jwt session in redis
    """

    key = f"jwt:{jit}"

    now = datetime.now(timezone.utc)

    ttl = int((expiration - now).total_seconds())

    print("================================")
    print("Redis key:", key)
    print("User ID:", user_id)
    print("Expiration:", expiration)
    print("TTL:", ttl)
    print("================================")

    if ttl <= 0:
        print("Token already expired")
        return

    redis_client.set(
        key,
        str(user_id),
        ex=ttl,
    )

    print("Token stored in redis:", redis_client.get(key))


def is_token_active(jit):
    """
    check whether JWT still exist in redis
    """
    key = f"jwt:{jit}"

    return redis_client.exists(key) == 1


def delete_token(jit):
    """
    Logout current JWT session
    """
    key = f"jwt:{jit}"
    redis_client.delete(key)



