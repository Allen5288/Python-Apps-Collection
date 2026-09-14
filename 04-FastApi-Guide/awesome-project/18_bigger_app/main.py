"""
18 - Bigger Applications: split the app into multiple files with APIRouter.

Run (from the project root):   fastapi dev 18_bigger_app/main.py

Layout:
    18_bigger_app/
    ├── __init__.py          makes it a package -> relative imports work
    ├── main.py              creates `app`, includes the routers   (THIS FILE)
    ├── dependencies.py      shared dependencies (auth, db, ...)
    ├── routers/
    │   ├── __init__.py
    │   ├── items.py         APIRouter for /items
    │   └── users.py         APIRouter for /users
    └── internal/
        ├── __init__.py
        └── admin.py         APIRouter we don't control, configured at include time

Rules of thumb:
    - Put prefix / tags / dependencies / responses ON the APIRouter itself
      (routers/items.py). Only pass them to include_router() when you cannot
      edit the router (internal/admin.py, third-party routers).
    - Global dependencies on FastAPI(...) apply to every route in every router.
    - Routers can include other routers (router.include_router) for nesting.
"""

from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

# Global dependency: every request must send ?token=jessica
app = FastAPI(dependencies=[Depends(get_query_token)])

# Routers that configured their own prefix/tags/dependencies:
app.include_router(users.router)
app.include_router(items.router)

# A router we "don't own": add prefix/tags/deps/responses at include time.
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


# The app itself can still have routes.
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
