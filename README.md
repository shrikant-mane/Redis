# 🔐 Django JWT Authentication with Redis

A Django REST Framework project demonstrating how to implement **JWT-based authentication with Redis** for managing active user sessions and supporting **instant JWT token revocation/logout**.

The project combines:

* Django
* Django REST Framework
* PyJWT
* Redis
* SQLite

The main objective of this project is to understand how JWT authentication can be combined with Redis to maintain server-side control over otherwise stateless JWT sessions.

---

## 📌 Project Overview

JWT (JSON Web Token) authentication is commonly used for securing REST APIs.

A traditional JWT is self-contained and stateless. Once issued, the server can normally validate the token until it expires. However, this creates a problem when a user wants to **log out immediately** or when a token becomes compromised.

This project solves that problem by storing the JWT's unique identifier (`jit`) in Redis.

### Authentication Flow

```text
                    ┌─────────────────┐
                    │      Client     │
                    └────────┬────────┘
                             │
                             │ Register
                             ▼
                    ┌─────────────────┐
                    │ Django / DRF    │
                    │ Register API    │
                    └─────────────────┘


                    ┌─────────────────┐
                    │      Client     │
                    └────────┬────────┘
                             │
                             │ Login
                             ▼
                    ┌─────────────────┐
                    │ Django / DRF    │
                    │    Login API    │
                    └────────┬────────┘
                             │
                             │ Generate JWT
                             ▼
                    ┌─────────────────┐
                    │     PyJWT       │
                    │ Create Token    │
                    └────────┬────────┘
                             │
                             │ Store JIT
                             ▼
                    ┌─────────────────┐
                    │      Redis      │
                    │ jwt:<JIT>       │
                    └─────────────────┘


Client Request
     │
     │ Authorization: Bearer <JWT>
     ▼
┌──────────────────────────┐
│ JWTAuthentication        │
└────────────┬─────────────┘
             │
             ├── Validate JWT
             │
             ├── Extract JIT
             │
             ├── Check JIT in Redis
             │
             └── Get User from Django DB
                       │
                       ▼
                 Authenticated API


Logout
   │
   ▼
Extract JIT
   │
   ▼
Delete jwt:<JIT>
   │
   ▼
Redis
   │
   ▼
Token becomes inactive immediately
```

---

# 🎯 Main Objective

The primary objective of this project is to demonstrate:

> **How Redis can be used alongside JWT authentication to maintain control over active JWT sessions and support immediate token revocation.**

When a user logs in:

1. Django authenticates the username and password.
2. A JWT is generated using PyJWT.
3. A unique token identifier (`jit`) is generated.
4. The token identifier is stored in Redis.
5. The JWT is returned to the client.
6. For protected APIs, the JWT is validated.
7. The token identifier is checked in Redis.
8. If the identifier exists, the request is considered authenticated.
9. During logout, the identifier is deleted from Redis.
10. The same JWT can no longer authenticate requests.

---

# 🧰 Technologies Used

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| Python                | Programming language            |
| Django                | Web framework                   |
| Django REST Framework | REST API development            |
| PyJWT                 | JWT creation and validation     |
| Redis                 | Active token/session management |
| SQLite                | Development database            |

The repository currently specifies Django 6.1, Django REST Framework 3.18.0, PyJWT 2.13.0, Redis Python client 8.1.0, and related dependencies in `requirements.txt`.

---

# 📂 Project Structure

```text
Redis/
│
├── accounts/
│   ├── migrations/
│   │
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── authetication.py
│   ├── jwt_utils.py
│   ├── models.py
│   ├── redis_client.py
│   ├── serializers.py
│   ├── tests.py
│   ├── token_service.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .gitignore
├── manage.py
└── requirements.txt
```

The current repository contains the `accounts` application and the `config` Django project configuration.

---

# 🔑 Authentication Architecture

The authentication implementation is divided into several components.

```text
Client
  │
  ▼
RegisterView
  │
  ▼
Django User
```

```text
Client
  │
  ▼
LoginView
  │
  ├── Django authenticate()
  │
  ▼
create_access_token()
  │
  ▼
JWT
  │
  ├── user_id
  ├── username
  ├── jit
  ├── issued-at
  └── expiration
  │
  ▼
store_token()
  │
  ▼
Redis
```

For protected APIs:

```text
Client
  │
  │ Authorization: Bearer <JWT>
  ▼
JWTAuthentication
  │
  ├── Extract Bearer token
  │
  ├── Decode JWT
  │
  ├── Extract JIT
  │
  ├── Check JIT in Redis
  │
  ├── Find User
  │
  └── Verify User is active
  │
  ▼
Authenticated Request
```

---

# 👤 User Registration

The project provides a registration API through `RegisterView`.

The serializer accepts:

```json
{
    "username": "shrikant",
    "email": "shrikant@example.com",
    "password": "password123"
}
```

The password is configured as a write-only serializer field, and the user is created using Django's `create_user()` method.

### Endpoint

```text
POST /accounts/register/
```

### Example Request

```json
{
    "username": "shrikant",
    "email": "shrikant@example.com",
    "password": "password123"
}
```

### Successful Response

```json
{
    "message": "User registered successfully",
    "user_id": 1,
    "username": "shrikant"
}
```

---

# 🔐 User Login

The login API authenticates the user using Django's authentication system.

```text
POST /accounts/login/
```

### Request

```json
{
    "username": "shrikant",
    "password": "password123"
}
```

The login flow is:

```text
Username + Password
        │
        ▼
Django authenticate()
        │
        ▼
    Valid User?
      /     \
    No       Yes
    │         │
    ▼         ▼
  Error    Create JWT
              │
              ▼
         Generate JIT
              │
              ▼
        Store JIT in Redis
              │
              ▼
        Return JWT
```

The implementation creates the JWT, stores the token identifier in Redis, and returns the access token to the client.

### Successful Response

```json
{
    "message": "User logged in successfully",
    "access_token": "<JWT_TOKEN>",
    "token_type": "Bearer",
    "expires_in": "<expiration>",
    "jit": "<JIT>"
}
```

---

# 🪙 JWT Implementation

JWT creation and decoding are implemented in:

```text
accounts/jwt_utils.py
```

The project generates a unique identifier for every token using UUID.

The JWT payload contains:

```json
{
    "user_id": 1,
    "user_name": "shrikant",
    "jit": "<unique-token-id>",
    "iat": "<issued-at-time>",
    "exp": "<expiration-time>"
}
```

The configured JWT algorithm is:

```text
HS256
```

The current access-token lifetime is configured as:

```text
3600 seconds
```

The JWT utility provides:

```python
create_access_token(user)
```

for generating tokens and:

```python
decode_access_token(token)
```

for validating and decoding tokens.

---

# 🧠 Why JIT Is Used

Each JWT contains a unique token identifier.

In this project, the identifier is stored in Redis using the format:

```text
jwt:<JIT>
```

For example:

```text
jwt:550e8400-e29b-41d4-a716-446655440000
```

Redis stores the user ID against that key.

Conceptually:

```text
Key                         Value
------------------------------------------------
jwt:<JIT>                   <user_id>
```

This provides a server-side way to determine whether a JWT is still active.

---

# 🔴 Redis Integration

Redis connectivity is implemented in:

```text
accounts/redis_client.py
```

The project connects to:

```text
Host: localhost
Port: 6379
Database: 0
```

The Redis Python client is configured with:

```text
decode_responses=True
```

The project uses Redis operations such as:

```python
redis_client.set(...)
redis_client.get(...)
redis_client.delete(...)
redis_client.exists(...)
```

---

# 🔄 Token Lifecycle Management

Token lifecycle operations are implemented in:

```text
accounts/token_service.py
```

The service provides three primary operations.

### 1. Store Token

```python
store_token(jit, user_id, expiration)
```

This stores the JWT identifier in Redis with a TTL based on the JWT expiration time.

```text
JWT
 │
 ├── JIT
 ├── User ID
 └── Expiration
        │
        ▼
      Redis
```

---

### 2. Check Token

```python
is_token_active(jit)
```

The application checks whether the corresponding Redis key exists.

Conceptually:

```python
jwt:<JIT> exists?
```

If it exists:

```text
Token Active
```

If it does not exist:

```text
Token Inactive / Logged Out
```

---

### 3. Delete Token

```python
delete_token(jit)
```

During logout, the Redis key associated with the JWT identifier is deleted.

```text
jwt:<JIT>
     │
     ▼
   DELETE
     │
     ▼
Token becomes inactive
```

---

# 🛡️ Custom JWT Authentication

Custom authentication is implemented in:

```text
accounts/authetication.py
```

The project extends:

```python
BaseAuthentication
```

through:

```python
JWTAuthentication
```

The authentication process is:

```text
Authorization Header
        │
        ▼
Bearer <JWT>
        │
        ▼
Extract JWT
        │
        ▼
Decode JWT
        │
        ▼
Extract JIT
        │
        ▼
Check JIT in Redis
        │
        ▼
Get User from Database
        │
        ▼
Check User.is_active
        │
        ▼
Authenticated User
```

The implementation rejects malformed authorization headers, invalid bearer authentication, expired/invalid JWTs, missing JIT values, tokens absent from Redis, nonexistent users, and inactive users.

---

# 🔒 Protected APIs

The project contains protected APIs that require authentication.

## Profile API

```text
GET /accounts/profile/
```

Example response:

```json
{
    "Message": "You are authenticated",
    "user_id": 1,
    "username": "shrikant",
    "email": "shrikant@example.com"
}
```

The endpoint uses DRF authentication/permission handling and returns information about the authenticated user.

---

# 📚 Protected Book API

The project also contains a protected book endpoint:

```text
GET /accounts/books/
```

Example response:

```json
{
    "Message": "Protected Book API",
    "username": "shrikant",
    "books": [
        {
            "id": 1,
            "title": "Python Programming"
        },
        {
            "id": 2,
            "title": "Java Programming"
        }
    ]
}
```

This endpoint demonstrates how the authenticated user's identity can be used when accessing a protected API.

---

# 🚪 Logout & JWT Revocation

Logout is implemented through:

```text
POST /accounts/logout/
```

The logout process is:

```text
Client
  │
  │ Bearer JWT
  ▼
JWTAuthentication
  │
  ▼
request.auth
  │
  ▼
Extract JIT
  │
  ▼
delete_token(JIT)
  │
  ▼
Redis DELETE
  │
  ▼
JWT becomes inactive
```

After the JIT is deleted from Redis, the same JWT will fail the Redis activity check even if the JWT itself has not reached its expiration time.

### Successful Response

```json
{
    "message": "User logged out successfully"
}
```

---

# 🔗 API Endpoints

| Method | Endpoint              | Authentication | Purpose                             |
| ------ | --------------------- | -------------- | ----------------------------------- |
| `POST` | `/accounts/register/` | ❌ No           | Register a new user                 |
| `POST` | `/accounts/login/`    | ❌ No           | Authenticate user and generate JWT  |
| `GET`  | `/accounts/profile/`  | ✅ Yes          | Access authenticated user profile   |
| `GET`  | `/accounts/books/`    | ✅ Yes          | Access protected book API           |
| `POST` | `/accounts/logout/`   | ✅ Yes          | Logout and revoke JWT through Redis |

These routes are defined in `accounts/urls.py`.

---

# 🧪 Testing with Postman

You can test the APIs using Postman.

## Step 1 — Register

```text
POST http://127.0.0.1:8000/accounts/register/
```

Body → `raw` → `JSON`

```json
{
    "username": "shrikant",
    "email": "shrikant@example.com",
    "password": "password123"
}
```

---

## Step 2 — Login

```text
POST http://127.0.0.1:8000/accounts/login/
```

Body:

```json
{
    "username": "shrikant",
    "password": "password123"
}
```

Copy the returned:

```text
access_token
```

---

## Step 3 — Access Profile

```text
GET http://127.0.0.1:8000/accounts/profile/
```

Add the following HTTP header:

```text
Authorization: Bearer <access_token>
```

Example:

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Step 4 — Access Books

```text
GET http://127.0.0.1:8000/accounts/books/
```

Header:

```text
Authorization: Bearer <access_token>
```

---

## Step 5 — Logout

```text
POST http://127.0.0.1:8000/accounts/logout/
```

Header:

```text
Authorization: Bearer <access_token>
```

The application extracts the token identifier and removes it from Redis.

---

## Step 6 — Try the Same Token Again

After logout, try:

```text
GET http://127.0.0.1:8000/accounts/profile/
```

with the same JWT.

The request should fail because the token's JIT no longer exists in Redis.

This demonstrates the key benefit of combining JWT with Redis:

```text
JWT is valid
      +
JIT exists in Redis
      =
Request Allowed
```

Whereas:

```text
JWT is valid
      +
JIT does NOT exist in Redis
      =
Request Rejected
```

---

# 🗄️ Database

The project currently uses SQLite for the Django database:

```text
db.sqlite3
```

The Django `User` model is used for user authentication and user information. The project does not define additional application models in `accounts/models.py` at the current stage.

---

# ⚙️ Configuration

The project currently contains the following Redis configuration:

```python
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
```

JWT configuration:

```python
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME = 3600
```

DRF is configured to use the custom authentication class:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authetication.JWTAuthentication',
    ],
}
```

The default permission is configured as:

```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',
]
```

---

# 🚀 Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.x
* Redis Server
* pip
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/shrikant-mane/Redis.git
```

Navigate into the project:

```bash
cd Redis
```

---

## 2. Create Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The repository currently includes these main dependencies:

```text
Django 6.1
djangorestframework 3.18.0
PyJWT 2.13.0
redis 8.1.0
```

---

# 🔴 Start Redis

The Django application expects Redis to be available on:

```text
localhost:6379
```

If Redis is installed through Homebrew on macOS:

```bash
brew services start redis
```

Check Redis:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

---

# 🐍 Run Django

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

---

# 🔍 Verify Redis Connection

The login implementation performs Redis connection checks using:

```python
redis_client.ping()
```

and prints Redis connection information during login.

You can also verify Redis independently:

```bash
redis-cli ping
```

Expected:

```text
PONG
```

---

# 🧪 Redis Token Example

After successful login, a token entry is stored in Redis using a key similar to:

```text
jwt:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

You can inspect Redis using:

```bash
redis-cli
```

Then:

```redis
KEYS *
```

You may see:

```text
jwt:<JIT>
```

To inspect the value:

```redis
GET jwt:<JIT>
```

The value represents the associated user ID.

---

# ⏱️ Token Expiration

The project calculates the Redis TTL from the JWT expiration time.

Conceptually:

```text
JWT Expiration
      │
      ▼
Calculate remaining lifetime
      │
      ▼
Redis TTL
```

Therefore, the Redis entry is intended to expire around the same time as the JWT.

The token service calculates the remaining seconds and uses Redis's expiration option when storing the token.

---

# 🔐 Security Concept

The project demonstrates two levels of JWT validation.

### Layer 1 — JWT Validation

PyJWT verifies:

* Signature
* Algorithm
* Expiration
* Token validity

### Layer 2 — Redis Validation

Redis verifies:

* Whether the JIT exists
* Whether the token has been revoked
* Whether the session is still active

Therefore:

```text
                JWT Authentication
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        PyJWT Validation     Redis Validation
             │                   │
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                Authenticated User
```

---

# 💡 Why Use Redis with JWT?

JWT provides a stateless authentication mechanism, but revoking an individual JWT before expiration is not naturally built into JWT itself.

Redis adds a lightweight server-side state layer.

### Without Redis

```text
Login
  │
  ▼
JWT
  │
  ▼
Client
  │
  ▼
JWT remains usable until expiration
```

### With Redis

```text
Login
  │
  ▼
JWT + JIT
  │
  ├──────────────► Client
  │
  ▼
Redis
  │
  ▼
Active Session


Logout
  │
  ▼
Delete JIT from Redis
  │
  ▼
Session Revoked
```

This makes Redis useful when an application needs immediate token/session invalidation.

---

# 🧱 Project Components

## `accounts/jwt_utils.py`

Responsible for:

* Creating JWTs
* Creating unique JIT values
* Adding user information to JWT payload
* Adding issued-at time
* Adding expiration time
* Decoding JWTs
* Handling expired/invalid tokens

---

## `accounts/redis_client.py`

Responsible for creating the Redis client connection.

```text
Redis Host
    ↓
localhost
    ↓
Port 6379
    ↓
Database 0
```

---

## `accounts/token_service.py`

Responsible for JWT session lifecycle:

```text
store_token()
is_token_active()
delete_token()
```

---

## `accounts/authetication.py`

Contains the custom:

```python
JWTAuthentication
```

It integrates:

```text
DRF
 +
PyJWT
 +
Redis
 +
Django User
```

---

## `accounts/serializers.py`

Contains:

```python
RegisterSerializer
```

It handles registration data and creates Django users using `create_user()`.

---

## `accounts/views.py`

Contains the API views:

```text
RegisterView
LoginView
ProfileView
BookView
LogoutView
```

---

# 📡 API Request Flow

### Registration

```text
POST /accounts/register/
        │
        ▼
RegisterSerializer
        │
        ▼
Django User
```

### Login

```text
POST /accounts/login/
        │
        ▼
authenticate()
        │
        ▼
create_access_token()
        │
        ▼
store_token()
        │
        ▼
Redis
        │
        ▼
JWT Response
```

### Protected API

```text
GET /accounts/profile/
        │
        ▼
Authorization Header
        │
        ▼
JWTAuthentication
        │
        ├── Decode JWT
        ├── Extract JIT
        ├── Check Redis
        └── Get User
        │
        ▼
Response
```

### Logout

```text
POST /accounts/logout/
        │
        ▼
JWTAuthentication
        │
        ▼
Extract JIT
        │
        ▼
delete_token()
        │
        ▼
Redis DELETE
        │
        ▼
Logout Successful
```

---

# 📋 API Summary

```text
┌───────────────────────────────┬──────────┬─────────────────┐
│ Endpoint                      │ Method   │ Authentication  │
├───────────────────────────────┼──────────┼─────────────────┤
│ /accounts/register/           │ POST     │ Public          │
│ /accounts/login/              │ POST     │ Public          │
│ /accounts/profile/            │ GET      │ JWT + Redis     │
│ /accounts/books/              │ GET      │ JWT + Redis     │
│ /accounts/logout/             │ POST     │ JWT + Redis     │
└───────────────────────────────┴──────────┴─────────────────┘
```

---

# 🎓 Learning Outcomes

This project helps demonstrate practical understanding of:

* Django project structure
* Django applications
* Django REST Framework
* APIView
* DRF authentication
* DRF permissions
* JWT
* PyJWT
* JWT payloads
* JWT expiration
* JIT/JTI-based token identification
* Redis connection
* Redis key-value storage
* Redis TTL
* Token revocation
* User authentication
* Bearer authentication
* Protected REST APIs
* Logout/session invalidation

---

# ⚠️ Production Considerations

This project is intended as a learning/development implementation.

Before using a similar architecture in production, consider:

### 1. Never hard-code secrets

The current project contains development JWT/Django secret values in `settings.py`. These should be moved to environment variables.

Example:

```python
import os

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
```

### 2. Disable Debug Mode

```python
DEBUG = False
```

### 3. Configure Allowed Hosts

Instead of:

```python
ALLOWED_HOSTS = []
```

configure the appropriate production domains/hosts.

### 4. Use HTTPS

Authentication tokens should be transmitted over HTTPS.

### 5. Use Environment Variables

Sensitive configuration should be stored outside source code:

```text
JWT_SECRET_KEY
REDIS_HOST
REDIS_PORT
REDIS_PASSWORD
DATABASE_URL
```

### 6. Avoid Debug Prints

The current implementation prints token/Redis debugging information. Production applications should use structured logging instead.

---

# 🔮 Future Enhancements

Possible improvements for this project:

* [ ] Refresh token implementation
* [ ] Access/refresh token rotation
* [ ] Token blacklist management
* [ ] Redis connection pooling configuration
* [ ] Redis authentication/password configuration
* [ ] Environment-based configuration
* [ ] Automated tests for authentication
* [ ] API documentation with Swagger/OpenAPI
* [ ] Docker Compose setup for Django + Redis
* [ ] PostgreSQL integration
* [ ] Rate limiting using Redis
* [ ] Session/device management
* [ ] Multiple-device logout
* [ ] Logout from all devices
* [ ] Production deployment configuration
* [ ] CI/CD pipeline

---

# 📖 Key Concept

The central concept demonstrated by this project is:

```text
                    JWT
                     +
                 Redis JIT
                     │
                     ▼
          Controlled Authentication
```

JWT handles the **identity and cryptographic validation**, while Redis provides **server-side control over whether the token is currently active**.

This combination allows an application to revoke a JWT immediately without waiting for its natural expiration.

---

# 👨‍💻 Author

**Shrikant Mane**

Python Developer | Django | Django REST Framework | REST APIs | Redis | JWT

---

# ⭐ Repository

GitHub Repository:

[Redis – Django JWT Authentication with Redis](https://github.com/shrikant-mane/Redis?utm_source=chatgpt.com)

---

## 📄 License

This project is intended for **learning, experimentation, and demonstration purposes**.
