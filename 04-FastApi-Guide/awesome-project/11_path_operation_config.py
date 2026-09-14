"""
11 - Path Operation Configuration: tags, summary, description, response_description,
     deprecated, operation_id, include_in_schema... and grouping the OpenAPI docs.

Run:   fastapi dev 11_path_operation_config.py   -> look at /docs

Everything here is about DOCUMENTATION / OpenAPI, not runtime behavior
(except `include_in_schema=False`, which just hides the route from docs).
"""

from enum import Enum

from fastapi import APIRouter, FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


# ---------------------------------------------------------------------------
# 1) tags -> groups endpoints in Swagger UI. summary/description -> texts.
#    Markdown is supported in description.
# ---------------------------------------------------------------------------
@app.post(
    "/items/",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=["items"],
    summary="Create an item",
    description="Create an item with all the information: **name**, description, price, tax and a set of unique tags",
    response_description="The created item",
)
async def create_item(item: Item):
    return item


# ---------------------------------------------------------------------------
# 2) The function DOCSTRING becomes the description (Markdown). Cleaner than a
#    long `description=` string.
# ---------------------------------------------------------------------------
@app.get("/items/", tags=["items"], summary="List items")
async def read_items():
    """
    Return all items.

    - Supports **Markdown**
    - Bullet points, `code`, etc.
    """
    return [{"name": "Foo", "price": 42}]


# An endpoint can belong to several tags.
@app.get("/users/", tags=["users", "admin"])
async def read_users():
    return [{"username": "johndoe"}]


# ---------------------------------------------------------------------------
# 3) Use an Enum for tags to avoid typos across a big project.
# ---------------------------------------------------------------------------
class Tags(Enum):
    items = "items"
    users = "users"


@app.get("/users/me", tags=[Tags.users])
async def read_user_me():
    return {"username": "me"}


# ---------------------------------------------------------------------------
# 4) deprecated=True: still works, shown greyed out in docs.
# ---------------------------------------------------------------------------
@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]


# ---------------------------------------------------------------------------
# 5) Hide from docs entirely (internal/health endpoints).
# ---------------------------------------------------------------------------
@app.get("/internal/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# 6) operation_id -> the name client generators (openapi-ts, etc.) use.
#    Default is "<function_name>_<path>_<method>" which is ugly.
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}", tags=["items"], operation_id="get_item_by_id")
async def read_item(item_id: int):
    return {"item_id": item_id}


# ---------------------------------------------------------------------------
# 7) Document extra responses so clients know the possible error shapes.
# ---------------------------------------------------------------------------
class Message(BaseModel):
    message: str


@app.get(
    "/items/{item_id}/detail",
    tags=["items"],
    response_model=Item,
    responses={
        404: {"model": Message, "description": "The item was not found"},
        200: {"description": "Item requested by ID", "content": {"application/json": {"example": {"name": "Foo", "price": 1}}}},
    },
)
async def read_item_detail(item_id: int):
    return Item(name="Foo", price=1)


# ---------------------------------------------------------------------------
# 8) Router-level grouping: put prefix/tags on the APIRouter itself so every
#    route in it is grouped under the same tag automatically.
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/")
async def list_orders():
    return []


@router.get("/{order_id}")
async def get_order(order_id: int):
    return {"order_id": order_id}


app.include_router(router)


# ---------------------------------------------------------------------------
# 9) Tag ORDER + descriptions in the docs via openapi_tags metadata on the app.
#    (Detailed in 22_metadata_docs.py; shown here because it completes grouping.)
# ---------------------------------------------------------------------------
app.openapi_tags = [
    {"name": "items", "description": "Operations with items."},
    {"name": "orders", "description": "Order management."},
    {"name": "users", "description": "Manage users. The **login** logic is also here."},
    {"name": "admin", "description": "Admin-only stuff."},
]
