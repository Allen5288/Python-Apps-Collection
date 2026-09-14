"""
07 - Response status codes (`status_code=`, `fastapi.status`) + response models.

Run:   fastapi dev 07_response_status.py

Common codes:
    200 OK (default)            201 Created (POST that creates)
    204 No Content (no body)    202 Accepted (background job started)
    3xx redirects               4xx client errors (400, 401, 403, 404, 422)
    5xx server errors

Use `from fastapi import status` so you write `status.HTTP_201_CREATED`
instead of the magic number 201 (autocomplete + readability).

Try:
    POST   /items/  {"name":"x","price":1}       -> 201
    DELETE /items/1                               -> 204, empty body
    GET    /items/1                               -> 200 with response filtered to ItemOut
    POST   /users/  {"username":"a","password":"secret","email":"a@b.co"} -> password NOT in response
    GET    /dynamic/2                             -> 201 vs 200 chosen at runtime
"""

from typing import Annotated, Any

from fastapi import FastAPI, Response, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()


class ItemIn(BaseModel):
    name: str
    price: float = Field(gt=0)
    secret_internal_note: str | None = None


class ItemOut(BaseModel):
    id: int
    name: str
    price: float


# ---------------------------------------------------------------------------
# 1) status_code on the decorator. Also documented in OpenAPI.
#    The return type -> ItemOut: validates + FILTERS the output (extra keys dropped).
# ---------------------------------------------------------------------------
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemIn) -> ItemOut:
    # secret_internal_note is not in ItemOut, so it never reaches the client
    return ItemOut(id=1, name=item.name, price=item.price)


# ---------------------------------------------------------------------------
# 2) 204 No Content: return None. FastAPI sends an empty body.
# ---------------------------------------------------------------------------
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    return None


# ---------------------------------------------------------------------------
# 3) response_model= when the RETURN TYPE differs from the public schema.
#    Here the function returns a dict (Any) but the API contract is ItemOut.
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}", response_model=ItemOut)
async def read_item(item_id: int) -> Any:
    return {"id": item_id, "name": "Plumbus", "price": 32.99, "leaked_field": "should not appear"}


# ---------------------------------------------------------------------------
# 4) Classic input/output model split: never echo passwords back.
# ---------------------------------------------------------------------------
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr  # needs `email-validator`, included in fastapi[standard]
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn) -> UserOut:
    # Return the UserIn object; the UserOut return type filters `password` out.
    return UserOut(**user.model_dump())


# ---------------------------------------------------------------------------
# 5) response_model_exclude_unset / include / exclude
#    -> only return the fields the client actually set (useful for PATCH).
# ---------------------------------------------------------------------------
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


items: dict[str, dict] = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
}


@app.get("/items-unset/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item_unset(item_id: str) -> Any:
    # GET /items-unset/foo -> {"name":"Foo","price":50.2}   (no defaults added)
    return items[item_id]


@app.get("/items-include/{item_id}", response_model=Item, response_model_include={"name", "description"})
async def read_item_include(item_id: str) -> Any:
    return items[item_id]


# ---------------------------------------------------------------------------
# 6) Change the status code DYNAMICALLY: inject `Response` and set it.
# ---------------------------------------------------------------------------
tasks: dict[str, str] = {"foo": "Listen to the Bar Fighters"}


@app.put("/dynamic/{task_id}", status_code=status.HTTP_200_OK)
async def upsert_task(task_id: str, name: Annotated[str, Field(min_length=1)], response: Response):
    if task_id in tasks:
        tasks[task_id] = name
        return {"task_id": task_id, "name": name, "created": False}
    tasks[task_id] = name
    response.status_code = status.HTTP_201_CREATED  # override the default 200
    return {"task_id": task_id, "name": name, "created": True}
