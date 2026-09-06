from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from django.contrib.auth import authenticate
from accounts.serializers import RegisterSerializer
from accounts.jwt_utils import create_access_token

from accounts.token_service import store_token, delete_token

from accounts.redis_client import redis_client

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully",
                    'user_id': user.id,
                    "username": user.username
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password :
            return Response(
                {
                    "message": "Please provide both username and password",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "message": "Invalid username or password",
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        #=======================
        # Create JWT
        #=======================
        token, jit, expiration = create_access_token(user)

        # =======================
        # Store JWT session in redis
        # =======================

        store_token(
            jit=jit,
            user_id=user.id,
            expiration=expiration
        )

        print("Redis connection:", redis_client)
        print("Redis ping:", redis_client.ping())
        print("Redis DB:", redis_client.connection_pool.connection_kwargs)

        return Response(
            {
                "message": "User logged in successfully",
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": expiration,
                "jit":jit
            }
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            {
                "Message":"You are authenticated",
                "user_id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        )


class BookView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            {
                "Message":"Protected Book API",
                "username":request.user.username,
                "books":[
                    {
                        'id':1,
                        'title':'Python Programming'
                    },
                    {
                      'id':2,
                        'title':'Java Programming'
                    },
                ],
            }
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        payload = request.auth
        jit = payload.get('jit')
        if not jit:
            return Response(
                {
                    "error": "JIT not found",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # delete jit
        delete_token(jit)

        return Response(
            {
                "message": "User logged out successfully",
            },
            status=status.HTTP_200_OK
        )
















