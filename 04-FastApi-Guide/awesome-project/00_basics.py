"""
00 - Basics: app, path params, route order, Enum, query params, request body.

Run:   fastapi dev 00_basics.py
Docs:  http://127.0.0.1:8000/docs

Try:
    GET  /
    GET  /items/5              -> 200 {"item_id": 5}
    GET  /items/abc            -> 422 (int validation fails)
    GET  /users/me             -> "the current user" (declared BEFORE /users/{user_id})
    GET  /users/42
    GET  /models/alexnet       -> Enum path param, only 3 values allowed
    GET  /users/1/items/foo?q=hi&short=true
    POST /items/  body: {"name": "Phone", "price": 100, "tax": 10}
"""

from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

# One FastAPI instance = one application. `fastapi dev` looks for a variable named `app`.
app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Simplest route. The decorator = HTTP method + path.
#    Returning a dict/list/str/Pydantic model -> FastAPI converts it to JSON.
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Hello World"}


# ---------------------------------------------------------------------------
# 2) Path parameter. `{item_id}` in the path becomes a function argument.
#    The type hint `int` does 3 things: parse "5" -> 5, validate (abc -> 422),
#    and document it in /docs.
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


# ---------------------------------------------------------------------------
# 3) Route ORDER matters. Routes are matched top-to-bottom.
#    "/users/me" must be declared BEFORE "/users/{user_id}", otherwise "me"
#    would be captured as user_id and fail int validation.
# ---------------------------------------------------------------------------
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}


# Declaring the SAME path twice: only the first one is ever used.
# (The second `read_users2` below is dead code; kept to demonstrate the pitfall.)
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


@app.get("/users")
async def read_users2():  # never reached
    return ["Bean", "Elfo"]


# ---------------------------------------------------------------------------
# 4) Predefined values with Enum.
#    Inherit from `str` too so the values are strings in OpenAPI and JSON.
#    /docs will show a dropdown with the 3 allowed values.
# ---------------------------------------------------------------------------
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # You receive a real Enum member, so you can compare with `is`.
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    # ...or via the raw string value.
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# ---------------------------------------------------------------------------
# 5) Path param that itself contains slashes: use the `:path` converter.
#    GET /files//home/johndoe/myfile.txt  -> file_path = "/home/johndoe/myfile.txt"
# ---------------------------------------------------------------------------
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# ---------------------------------------------------------------------------
# 6) Query parameters = any function argument that is NOT in the path.
#    - With a default value -> optional  (q, short)
#    - Without a default    -> required  (needy)
#    Types are converted: ?short=true / 1 / on / yes  all become True.
# ---------------------------------------------------------------------------
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,  # path
    item_id: str,  # path
    q: str | None = None,  # optional query
    short: bool = False,  # optional query with default
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


@app.get("/search")
async def search(needy: str, skip: int = 0, limit: int = 10):
    # `needy` has no default -> calling /search without ?needy=... gives 422
    return {"needy": needy, "skip": skip, "limit": limit}


# ---------------------------------------------------------------------------
# 7) Request body with a Pydantic model.
#    A parameter typed as a BaseModel subclass is read from the JSON body.
#    FastAPI validates it, gives you a typed object, and documents the schema.
# ---------------------------------------------------------------------------
class Item(BaseModel):
    name: str
    description: str | None = None  # optional field
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    # `.model_dump()` -> plain dict (Pydantic v2 API; `.dict()` is deprecated)
    item_dict = item.model_dump()
    if item.tax is not None:
        item_dict.update({"price_with_tax": item.price + item.tax})
    return item_dict


# Body + path + query in ONE function. FastAPI figures out where each comes from:
#   - declared in the path            -> path param
#   - singular type (int, str, ...)   -> query param
#   - Pydantic model                  -> request body
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
