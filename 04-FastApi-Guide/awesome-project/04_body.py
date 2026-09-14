"""
04 - Body: multiple body params, Body(), Field(), nested models, list bodies.

Run:   fastapi dev 04_body.py

Rules of thumb:
    - ONE Pydantic model param       -> the whole JSON body IS that model.
    - TWO+ Pydantic model params     -> body is an object with one key per param name.
    - Singular value in the body     -> wrap it with `Body()` (otherwise it's a query).
    - `embed=True`                   -> force a single model to be nested under its name.

Try (POST/PUT with JSON):
    PUT  /items/1            {"name":"Foo","price":42}
    PUT  /items/multi/1      {"item":{"name":"Foo","price":42},"user":{"username":"allen"}}
    PUT  /items/singular/1   {"item":{...},"user":{...},"importance":5}
    PUT  /items/embed/1      {"item":{"name":"Foo","price":42}}
    PUT  /items/nested/1     {"name":"Foo","price":42,"tags":["a","b"],"image":{"url":"https://x/y.png","name":"pic"}}
    POST /images/multiple/   [{"url":"https://x/1.png","name":"a"},{"url":"https://x/2.png","name":"b"}]
    POST /index-weights/     {"1": 0.5, "2": 1.5}
"""

from typing import Annotated

from fastapi import Body, FastAPI, Path
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


# ---------------------------------------------------------------------------
# Models. `Field()` adds validation/metadata to model attributes.
# ---------------------------------------------------------------------------
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


# ---------------------------------------------------------------------------
# 1) Single body param -> body == Item.   Path + Query + Body mixed.
# ---------------------------------------------------------------------------
@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(ge=1)],
    item: Item,  # body
    q: str | None = None,  # query
):
    return {"item_id": item_id, "q": q, "item": item}


# ---------------------------------------------------------------------------
# 2) MULTIPLE body params -> FastAPI expects:
#    {"item": {...}, "user": {...}}
# ---------------------------------------------------------------------------
@app.put("/items/multi/{item_id}")
async def update_item_multi(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}


# ---------------------------------------------------------------------------
# 3) Singular value inside the body: `importance` would be a QUERY param
#    by default (it's an int). `Body()` tells FastAPI to read it from the body.
#    Expected body: {"item": {...}, "user": {...}, "importance": 5}
# ---------------------------------------------------------------------------
@app.put("/items/singular/{item_id}")
async def update_item_singular(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,  # still a query param
):
    return {"item_id": item_id, "item": item, "user": user, "importance": importance, "q": q}


# ---------------------------------------------------------------------------
# 4) embed=True: a SINGLE model but you want  {"item": {...}}  instead of {...}
# ---------------------------------------------------------------------------
@app.put("/items/embed/{item_id}")
async def update_item_embed(item_id: int, item: Annotated[Item, Body(embed=True)]):
    return {"item_id": item_id, "item": item}


# ---------------------------------------------------------------------------
# 5) Nested models + special types (HttpUrl validates it's a real URL).
#    - `tags: set[str]` de-duplicates automatically.
#    - `image: Image | None` -> nested object.
#    - `images: list[Image]` -> list of nested objects.
# ---------------------------------------------------------------------------
class Image(BaseModel):
    url: HttpUrl
    name: str


class ItemNested(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
    images: list[Image] | None = None


@app.put("/items/nested/{item_id}")
async def update_item_nested(item_id: int, item: ItemNested):
    return {"item_id": item_id, "item": item}


# Deeply nested: Offer -> list[ItemNested] -> list[Image]
class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[ItemNested]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


# ---------------------------------------------------------------------------
# 6) Body that is a top-level LIST  (JSON array):  [{...}, {...}]
# ---------------------------------------------------------------------------
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


# Body that is a dict with int keys (JSON keys are always strings; Pydantic
# converts "1" -> 1 for you):  {"1": 0.5, "2": 1.5}
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights


# ---------------------------------------------------------------------------
# 7) Body of plain values with constraints, without a wrapper model:
#    POST /ids/   [1, 2, 3]   (must have at least 1 element)
# ---------------------------------------------------------------------------
@app.post("/ids/")
async def create_ids(ids: Annotated[list[int], Field(min_length=1), Body()]):
    return {"count": len(ids), "ids": ids}
