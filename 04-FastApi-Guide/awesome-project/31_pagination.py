"""31 - Pagination: list endpoints that stay fast and honest as data grows.

Topic: a list endpoint that returns every row works fine with 24
products and falls over with 24,000. Pagination is the fix: the
client asks for a page (`skip` + `limit`), the server answers with
that page plus the metadata the client needs to ask for the next
one — the total count, and whether another page exists. The
validation matters as much as the slicing: `limit` is bounded, so
one client cannot ask for a million rows and make the server build
a million-row response.

This example uses offset pagination (`skip`/`limit`), the simplest
shape and the right default for admin lists and small catalogues.
Its limit is honest, too: deep pages get slow (the database still
scans the skipped rows), and a row inserted mid-browse shifts every
later page. When the list is a live feed — or past a few thousand
rows — cursor pagination (an opaque `after=<id>` token) is the
better shape; see the note at the bottom.

Run:
    fastapi dev 31_pagination.py   # -> http://127.0.0.1:8000/docs

Try:
    curl http://127.0.0.1:8000/products
    curl "http://127.0.0.1:8000/products?skip=10&limit=5"
    curl "http://127.0.0.1:8000/products?limit=500"   # 422 — limit is at most 100
    curl http://127.0.0.1:8000/products/p-017

Daily note, 2026-11-28: the response carries the metadata, not the
client's guesswork — `total` and `has_more` mean the client never
has to request one more page just to find out the list ended.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="31 - Pagination")

MAX_LIMIT = 100
DEFAULT_LIMIT = 10


class Product(BaseModel):
    """One catalogue row. In a real app this comes from the database
    (see 17, SQLModel); here it is an in-memory list so the paging
    logic is the thing under test, not the query."""

    id: str
    name: str
    category: str
    price_aud: int


# 24 rows: enough for three default pages (10 + 10 + 4), so the
# last-page behaviour (has_more False, fewer items than the limit)
# is visible without scrolling through hundreds of rows.
_CATEGORIES = ["Kitchen", "Lighting", "Textiles", "Decor"]
PRODUCTS = [
    Product(
        id=f"p-{i:03d}",
        name=f"Product {i:02d}",
        category=_CATEGORIES[(i - 1) % len(_CATEGORIES)],
        price_aud=10 + i,
    )
    for i in range(1, 25)
]


class Page(BaseModel):
    """The envelope every list endpoint returns. `items` is the
    page; `total` is the whole list; `has_more` tells the client
    whether asking for the next page is worth it. The client
    paginates with `skip + limit`, never by guessing."""

    total: int
    skip: int
    limit: int
    has_more: bool
    items: list[Product]


@app.get("/products", response_model=Page)
def list_products(
    skip: int = Query(0, ge=0, description="Rows to skip — page * page size"),
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description=f"Rows per page, at most {MAX_LIMIT}",
    ),
):
    """Slice the list and report the metadata. The slice itself is
    one line; the value is the envelope around it, and the bound on
    `limit` — `le=100` rejects rather than silently clamps, so the
    client knows its request was refused instead of receiving
    fewer rows than it asked for. Without the bound,
    `?limit=1000000` is a denial of service the client opts into
    by accident."""
    page_items = PRODUCTS[skip : skip + limit]
    return Page(
        total=len(PRODUCTS),
        skip=skip,
        limit=limit,
        has_more=skip + len(page_items) < len(PRODUCTS),
        items=page_items,
    )


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """One row by id — the detail view a list page links to. A
    missing id is a 404, not an empty page: a page can legitimately
    be empty (skip past the end), a single item cannot."""
    for product in PRODUCTS:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="product not found")


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Rules to remember (run with: uv run pytest 31_pagination.py -v
# only if you add tests — the snippet below is the pattern to copy):
#
#     from fastapi.testclient import TestClient
#
#     def test_default_page_is_ten_items_with_more_to_come():
#         with TestClient(app) as client:
#             page = client.get("/products").json()
#             assert page["total"] == 24
#             assert len(page["items"]) == 10
#             assert page["has_more"] is True
#
#     def test_last_page_reports_no_more_pages():
#         with TestClient(app) as client:
#             page = client.get("/products?skip=20&limit=10").json()
#             assert len(page["items"]) == 4
#             assert page["has_more"] is False
#
#     def test_limit_over_the_max_is_rejected():
#         with TestClient(app) as client:
#             assert client.get("/products?limit=500").status_code == 422
#
#     def test_negative_skip_is_rejected():
#         with TestClient(app) as client:
#             assert client.get("/products?skip=-1").status_code == 422
#
#     def test_unknown_product_is_404():
#         with TestClient(app) as client:
#             assert client.get("/products/p-999").status_code == 404
#
# - Always return the total with the page. Without it the client
#   cannot render "page 2 of 5" or a progress bar — it can only
#   keep fetching until a page comes back empty.
# - `has_more` is computed from the data, not from "the page was
#   full": a page that happens to end exactly on a boundary (20 of
#   20) has no more pages, and a full page must not claim otherwise.
# - Bound `limit` server-side with `le=`. A client that asks for
#   a million rows is usually a bug; the bound turns it into a 422
#   instead of a slow response and a large bill. Rejecting beats
#   silently clamping: the client learns its request was refused
#   instead of quietly receiving fewer rows than it asked for.
# - Offset pagination shifts when rows are inserted or deleted
#   mid-browse: the client can see a row twice or miss one. For a
#   feed, or a list past a few thousand rows, use cursor
#   pagination instead — `?after=<last seen id>` — where the
#   database seeks to the id instead of scanning skipped rows.
# ---------------------------------------------------------------------------
