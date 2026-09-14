"""
Users router. Only prefix + tags on the router, no extra dependencies
(the global ?token=jessica from main.py still applies).

    curl "http://127.0.0.1:8000/users/?token=jessica"
    curl "http://127.0.0.1:8000/users/me?token=jessica"
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


# Declared BEFORE /{username} so "me" is not captured as a username.
@router.get("/me")
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/{username}")
async def read_user(username: str):
    return {"username": username}
