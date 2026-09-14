"""
12 - JSON Compatible Encoder: `jsonable_encoder`.

Run:   fastapi dev 12_jsonable_encoder.py

Problem: `json.dumps()` can't handle datetime, UUID, Decimal, Pydantic models, sets...
`jsonable_encoder(obj)` converts ANY of those into plain dict/list/str/int/float/None
that `json.dumps` accepts. FastAPI uses it internally when you return objects.

When do YOU call it manually?
    - Storing data in a JSON-only store (fake DB dict, Redis, a .json file)
    - Building a `JSONResponse(content=...)` by hand
    - Passing data to a background task / message queue
    - Custom exception handlers (see 10_error_handling.py)

Try:
    PUT /items/foo  {"title":"Hi","timestamp":"2026-09-14T10:00:00Z","description":"x"}
    GET /items/foo
    GET /demo
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# A "database" that only accepts JSON-compatible data (like a real doc store).
fake_db: dict[str, dict] = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


# ---------------------------------------------------------------------------
# 1) Store a Pydantic model as JSON-compatible dict.
#    item.timestamp is a datetime -> becomes an ISO 8601 string.
# ---------------------------------------------------------------------------
@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return json_compatible_item_data


@app.get("/items/{id}")
def read_item(id: str):
    return fake_db.get(id, {"error": "not found"})


# ---------------------------------------------------------------------------
# 2) Everything jsonable_encoder can handle, in one place.
# ---------------------------------------------------------------------------
class Nested(BaseModel):
    id: UUID
    amount: Decimal
    tags: set[str]


@app.get("/demo")
def demo():
    raw = {
        "when": datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc),  # -> "2026-09-14T10:00:00Z"
        "uuid": uuid4(),  # -> string
        "decimal": Decimal("19.99"),  # -> 19.99 (float) by default
        "set": {"a", "b"},  # -> list
        "bytes": b"hello",  # -> "hello"
        "model": Nested(id=uuid4(), amount=Decimal("1.5"), tags={"x"}),  # -> dict
        "none": None,
    }
    encoded = jsonable_encoder(raw)
    # Now it's safe for json.dumps / JSONResponse
    return JSONResponse(content=encoded)


# ---------------------------------------------------------------------------
# 3) Useful options:
#    - exclude_unset=True : drop fields the client didn't send (PATCH semantics)
#    - by_alias=True      : use Field(alias=...) names as keys
#    - exclude={"secret"} : drop specific keys
# ---------------------------------------------------------------------------
class Profile(BaseModel):
    username: str
    bio: str | None = None
    secret: str = "hidden"


@app.post("/profiles/")
def create_profile(profile: Profile):
    return {
        "full": jsonable_encoder(profile),
        "exclude_unset": jsonable_encoder(profile, exclude_unset=True),
        "exclude_secret": jsonable_encoder(profile, exclude={"secret"}),
    }
