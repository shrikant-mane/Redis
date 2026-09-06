import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from django.conf import settings

def create_access_token(user):
    """
    Create JWT for user
    """

    now = datetime.now(timezone.utc)
    expiration = now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)

    jit = str(uuid4())

    payload = {
        "user_id": user.id,
        "user_name": user.username,
        "jit":jit,
        "iat": now,
        "exp": expiration
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )

    print("================================")
    print("JWT TIME DEBUG")
    print("Now UTC:", now)
    print("Expiration UTC:", expiration)
    print("Lifetime:", settings.JWT_ACCESS_TOKEN_LIFETIME)
    print("JTI:", jit)
    print("================================")

    return token, jit, expiration



def decode_access_token(token):
    """
    Decode JWT for user
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise ValueError('JWT token has expired')

    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')

    return payload




