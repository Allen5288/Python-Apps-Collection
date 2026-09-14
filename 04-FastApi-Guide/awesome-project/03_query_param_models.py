"""
03 - Query Parameter Models (group related query params into a Pydantic model).

Run:   fastapi dev 03_query_param_models.py

Instead of repeating `limit`, `offset`, `order_by` in every endpoint, declare
them ONCE in a BaseModel and use `Annotated[Model, Query()]`.

Try:
    GET /items/                                   -> defaults
    GET /items/?limit=5&offset=10&order_by=updated_at&tags=a&tags=b
    GET /items/?limit=0                           -> 422 (Field gt=0)
    GET /items/?order_by=name                     -> 422 (Literal only allows 2 values)
    GET /items/?tool=plumbus                      -> 422 (extra="forbid")
"""

from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) The model. `Field()` in Pydantic == validation + metadata for a model field.
#    `Literal[...]` restricts a value to a fixed set (like a mini-Enum).
# ---------------------------------------------------------------------------
class FilterParams(BaseModel):
    # forbid unknown query params -> /items/?foo=1 returns 422
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100, description="Page size")
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []  # ?tags=a&tags=b


# ---------------------------------------------------------------------------
# 2) Use it. FastAPI reads every field from the query string and validates.
# ---------------------------------------------------------------------------
@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    # you get a fully typed object back
    return filter_query


# ---------------------------------------------------------------------------
# 3) Reusable across many endpoints: define an alias type once.
# ---------------------------------------------------------------------------
FilterQuery = Annotated[FilterParams, Query()]


@app.get("/users/")
async def read_users(filter_query: FilterQuery):
    return {"resource": "users", **filter_query.model_dump()}


@app.get("/orders/")
async def read_orders(filter_query: FilterQuery):
    return {"resource": "orders", **filter_query.model_dump()}


# ---------------------------------------------------------------------------
# 4) A model WITHOUT extra="forbid": unknown params are silently ignored.
#    GET /loose/?whatever=1  -> ok
# ---------------------------------------------------------------------------
class LooseParams(BaseModel):
    q: str | None = None
    page: int = Field(1, ge=1)


@app.get("/loose/")
async def read_loose(params: Annotated[LooseParams, Query()]):
    return params
