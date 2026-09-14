"""
Admin router. Imagine this comes from another team / package and we CANNOT edit it,
so it has no prefix/tags/dependencies. main.py adds them in include_router().

    curl -X POST "http://127.0.0.1:8000/admin/?token=jessica" -H "X-Token: fake-super-secret-token"
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}
