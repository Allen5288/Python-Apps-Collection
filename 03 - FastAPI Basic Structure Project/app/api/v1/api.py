from fastapi import APIRouter

from .endpoints import users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
