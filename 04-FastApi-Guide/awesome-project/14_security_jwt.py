"""
14 - Security: OAuth2 password flow + Bearer JWT tokens + "get current user".

Run:   fastapi dev 14_security_jwt.py
Deps:  pyjwt, pwdlib[argon2]   (uv add pyjwt "pwdlib[argon2]")

Flow:
    1. Client POSTs username+password as FORM data to /token  (OAuth2 spec)
    2. Server verifies the password hash, returns {"access_token": <JWT>, "token_type": "bearer"}
    3. Client sends `Authorization: Bearer <JWT>` on every request
    4. `get_current_user` dependency decodes the JWT and loads the user

In /docs click "Authorize", enter  johndoe / secret  -> Swagger stores the token
and adds the header for you.

curl:
    curl -X POST http://127.0.0.1:8000/token -d "username=johndoe&password=secret"
    curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <paste token>"
    curl http://127.0.0.1:8000/users/me            -> 401 Not authenticated
    login as alice / secret  then GET /users/me   -> 400 Inactive user
    GET /admin/               -> 403 unless johndoe (scope check example)
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config. In real life: SECRET_KEY from env (`openssl rand -hex 32`).
# ---------------------------------------------------------------------------
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwdlib: modern replacement for passlib. `.recommended()` = Argon2.
password_hash = PasswordHash.recommended()

# tokenUrl = the path the CLIENT uses to get a token (relative URL is fine).
# This object is a DEPENDENCY: it reads `Authorization: Bearer xxx` and returns
# the raw token string, or raises 401 if the header is missing.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# ---------------------------------------------------------------------------
# "Database"
# ---------------------------------------------------------------------------
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": password_hash.hash("secret"),  # hash at startup for the demo
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": password_hash.hash("secret"),
        "disabled": True,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str  # never returned to clients (response type is `User`)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_user(db: dict, username: str) -> UserInDB | None:
    if username in db:
        return UserInDB(**db[username])
    return None


def authenticate_user(db: dict, username: str, password: str) -> UserInDB | None:
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})  # standard JWT claim; PyJWT checks it on decode
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Dependencies: token -> user -> active user
# ---------------------------------------------------------------------------
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # required by the spec for 401
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")  # "sub" = subject = who the token is about
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:  # expired, bad signature, malformed...
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[UserInDB, Depends(get_current_user)]) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Reusable alias: put this on any endpoint that needs a logged-in user.
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # OAuth2PasswordRequestForm = form fields: username, password, (scope, grant_type, client_id, client_secret)
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_users_me(current_user: CurrentUser) -> User:
    # return type `User` strips hashed_password from the response
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: CurrentUser):
    return [{"item_id": "Foo", "owner": current_user.username}]


# Simple role/permission check built on top of the user dependency.
def require_admin(current_user: CurrentUser) -> UserInDB:
    if current_user.username != "johndoe":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user


@app.get("/admin/", dependencies=[Depends(require_admin)])
async def admin_area():
    return {"message": "welcome, admin"}


# Public endpoint: no dependency -> no token needed.
@app.get("/public")
async def public():
    return {"message": "anyone can see this"}
