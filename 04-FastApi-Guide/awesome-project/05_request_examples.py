"""
05 - Declare Request Example Data (shown in /docs "Example Value").

Run:   fastapi dev 05_request_examples.py   -> open /docs and expand each endpoint.

Three places to put examples (from most to least common):
    1. `model_config = {"json_schema_extra": {"examples": [...]}}`  on the model
    2. `Field(examples=[...])`                                     per field
    3. `Body(examples=[...])` / `Query(examples=[...])`            per parameter
    4. `Body(openapi_examples={...})`  -> MULTIPLE named examples with a dropdown
       in Swagger UI (summary / description / value / externalValue).
"""

from typing import Annotated

from fastapi import Body, FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Whole-model example via model_config -> goes into the JSON Schema.
# ---------------------------------------------------------------------------
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


@app.put("/items/model-example/{item_id}")
async def update_item_model_example(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}


# ---------------------------------------------------------------------------
# 2) Per-field examples with Field(examples=[...]).
# ---------------------------------------------------------------------------
class ItemFieldExamples(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])


@app.put("/items/field-examples/{item_id}")
async def update_item_field_examples(item_id: int, item: ItemFieldExamples):
    return {"item_id": item_id, "item": item}


# ---------------------------------------------------------------------------
# 3) Example on the parameter with Body(examples=[...]) (a list of examples).
# ---------------------------------------------------------------------------
class PlainItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/body-examples/{item_id}")
async def update_item_body_examples(
    item_id: int,
    item: Annotated[
        PlainItem,
        Body(
            examples=[
                {"name": "Foo", "description": "A very nice Item", "price": 35.4, "tax": 3.2},
                {"name": "Bar", "price": "35.4"},  # strings get converted
            ]
        ),
    ],
):
    return {"item_id": item_id, "item": item}


# ---------------------------------------------------------------------------
# 4) MULTIPLE NAMED examples -> dropdown in Swagger UI.
#    Keys are example names; each has summary / description / value.
# ---------------------------------------------------------------------------
@app.put("/items/openapi-examples/{item_id}")
async def update_item_openapi_examples(
    item_id: int,
    item: Annotated[
        PlainItem,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {"name": "Foo", "description": "A very nice Item", "price": 35.4, "tax": 3.2},
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {"name": "Bar", "price": "35.4"},
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {"name": "Baz", "price": "thirty five point four"},
                },
            }
        ),
    ],
):
    return {"item_id": item_id, "item": item}


# ---------------------------------------------------------------------------
# 5) Examples also work for Query / Path / Header / Cookie.
# ---------------------------------------------------------------------------
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(examples=["plumbus", "portal gun"])] = None):
    return {"q": q}
