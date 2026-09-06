import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.models import User

from accounts.jwt_utils import decode_access_token
from accounts.token_service import is_token_active

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        part = auth_header.split()

        if len(part) != 2:
            raise AuthenticationFailed('Invalid Authorization header')

        if part[0].lower() != 'bearer':
            raise AuthenticationFailed(
                "Authorization must use bearer token"
            )

        token = part[1]


        #===================
        #1. Validate JWT using PyJWT
        #===================

        try:
            payload = decode_access_token(token)

        except ValueError as e:
            raise AuthenticationFailed(str(e))


        # ===================
        # 2. Get JIT
        # ===================
        jit = payload.get('jit')
        if not jit:
            raise AuthenticationFailed("Token does not contain 'jit'")

        # ===================
        # 3. Check Redis
        # ===================

        if not is_token_active(jit):
            raise AuthenticationFailed("Token has been logged out or is inactive")


        # ===================
        # 2. Get JIT
        # ===================

        user_id = payload.get('user_id')

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            raise AuthenticationFailed("User does not exist")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return user, payload








