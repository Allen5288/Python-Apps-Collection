"""
01 - Query Parameters and String Validations (Query + Annotated).

Run:   fastapi dev 01_query_validation.py

Why `Annotated[type, Query(...)]`?
    - The Python type stays the real type (editors / type checkers are happy).
    - `Query(...)` adds validation + docs metadata.
    - The default value stays as a normal Python default (`= None`).
    This is the recommended style. The old style `q: str = Query(None, max_length=50)`
    still works but is discouraged.

Try:
    GET /items/?q=abc                 -> ok
    GET /items/?q=ab                  -> 422 (min_length=3)
    GET /items/?q=hello%20world       -> 422 (pattern requires letters/digits only)
    GET /items/required?q=x
    GET /items/list?q=a&q=b&q=c       -> list of values
    GET /items/alias?item-query=foo   -> python name `item_query`, URL name `item-query`
    GET /items/hidden?secret=1
"""

from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Optional query with string constraints.
# ---------------------------------------------------------------------------
@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            pattern="^[a-zA-Z0-9]+$",  # regex; `regex=` is the deprecated name
            title="Query string",
            description="Search text for the items, letters and digits only",
        ),
    ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# ---------------------------------------------------------------------------
# 2) REQUIRED query param: just omit the default.
#    You can still attach Query() metadata. Do NOT use `= ...` (Ellipsis).
# ---------------------------------------------------------------------------
@app.get("/items/required")
async def read_items_required(q: Annotated[str, Query(min_length=1)]):
    return {"q": q}


# Required but allowed to be null:  ?q=  is invalid (empty str), but the param
# must be present. Type `str | None` without a default = required-nullable.
@app.get("/items/required-nullable")
async def read_items_required_nullable(q: Annotated[str | None, Query(min_length=1)]):
    return {"q": q}


# ---------------------------------------------------------------------------
# 3) List / multiple values:  ?q=a&q=b  -> ["a", "b"]
#    You MUST use Query() here, otherwise a `list` type is treated as a body.
# ---------------------------------------------------------------------------
@app.get("/items/list")
async def read_items_list(q: Annotated[list[str] | None, Query()] = None):
    return {"q": q}


# list with default values
@app.get("/items/list-default")
async def read_items_list_default(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    return {"q": q}


# ---------------------------------------------------------------------------
# 4) Alias: the URL uses `item-query` (not a valid Python identifier).
# ---------------------------------------------------------------------------
@app.get("/items/alias")
async def read_items_alias(item_query: Annotated[str | None, Query(alias="item-query")] = None):
    return {"item_query": item_query}


# ---------------------------------------------------------------------------
# 5) Deprecate a param (still works, shown crossed-out in /docs)
#    and hide a param from the docs entirely.
# ---------------------------------------------------------------------------
@app.get("/items/hidden")
async def read_items_hidden(
    old: Annotated[str | None, Query(deprecated=True)] = None,
    secret: Annotated[str | None, Query(include_in_schema=False)] = None,
):
    return {"old": old, "secret": secret}


# ---------------------------------------------------------------------------
# 6) Custom validation with Pydantic's AfterValidator.
#    Runs AFTER the basic type validation. Raise ValueError -> 422 with message.
# ---------------------------------------------------------------------------
from pydantic import AfterValidator  # noqa: E402  (import here to keep the topic together)


def check_valid_id(id: str) -> str:
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items/custom-validation")
async def read_items_custom(id: Annotated[str | None, AfterValidator(check_valid_id)] = None):
    return {"id": id}


# ---------------------------------------------------------------------------
# 7) Numeric constraints work on query params too (gt, ge, lt, le).
# ---------------------------------------------------------------------------
@app.get("/items/paged")
async def read_items_paged(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
):
    return {"skip": skip, "limit": limit}
