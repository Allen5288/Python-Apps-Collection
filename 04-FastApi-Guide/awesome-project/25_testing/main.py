"""
25 - The app under test. See test_main.py next to this file.

Run the app:    fastapi dev 25_testing/main.py
Run the tests:  uv run pytest 25_testing -v
"""

from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

fake_secret_token = "coneofsilence"

fake_db: dict[str, dict] = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

app = FastAPI()


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None


@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str, x_token: Annotated[str, Header()]):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: Item, x_token: Annotated[str, Header()]):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        raise HTTPException(status_code=409, detail="Item already exists")
    fake_db[item.id] = item.model_dump()
    return item
