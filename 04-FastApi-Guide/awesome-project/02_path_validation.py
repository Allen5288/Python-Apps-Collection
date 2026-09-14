"""
02 - Path Parameters and Numeric Validations (Path + Annotated).

Run:   fastapi dev 02_path_validation.py

`Path()` is like `Query()` but for path params. Path params are ALWAYS required
(they are part of the URL), so they never have a default.

Numeric validators:
    gt  -> greater than            ge -> greater than or equal
    lt  -> less than               le -> less than or equal

Try:
    GET /items/1
    GET /items/0          -> 422 (ge=1)
    GET /items/1001       -> 422 (le=1000)
    GET /items/5/size/2.5
    GET /items/5/size/0   -> 422 (gt=0)
"""

from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Path with title/description + numeric bounds.
#    Mixing Path and Query in one signature: with Annotated the ORDER of
#    parameters doesn't matter (no "default before non-default" problem).
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=1000)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# ---------------------------------------------------------------------------
# 2) Float validation: gt / lt work with floats as well.
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}/size/{size}")
async def read_item_size(
    item_id: Annotated[int, Path(ge=1)],
    size: Annotated[float, Path(gt=0, lt=10.5)],
):
    return {"item_id": item_id, "size": size}


# ---------------------------------------------------------------------------
# 3) String path param constraints (min/max length, pattern).
#    GET /users/ab      -> 422
#    GET /users/allen   -> ok
# ---------------------------------------------------------------------------
@app.get("/users/{username}")
async def read_user(
    username: Annotated[str, Path(min_length=3, max_length=20, pattern="^[a-z]+$")],
):
    return {"username": username}
