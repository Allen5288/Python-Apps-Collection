"""
Items router. Everything shared by these routes is declared ON the router:
prefix, tags, dependencies, default responses.

Try (all need ?token=jessica because of the global dependency in main.py,
and X-Token because of the router dependency):
    curl "http://127.0.0.1:8000/items/?token=jessica" -H "X-Token: fake-super-secret-token"
    curl "http://127.0.0.1:8000/items/plumbus?token=jessica" -H "X-Token: fake-super-secret-token"
    curl -X PUT "http://127.0.0.1:8000/items/gun?token=jessica" -H "X-Token: fake-super-secret-token"   -> 403
"""

from fastapi import APIRouter, Depends, HTTPException

# `..` = go up one package: 18_bigger_app/dependencies.py
from ..dependencies import get_token_header

router = APIRouter(
    prefix="/items",  # every path below is relative to this
    tags=["items"],
    dependencies=[Depends(get_token_header)],  # applies to every route in this router
    responses={404: {"description": "Not found"}},  # documented for every route
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return fake_items_db


@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


# Per-route extras are MERGED with the router's: tags -> ["items", "custom"],
# responses -> {404, 403}.
@router.put("/{item_id}", tags=["custom"], responses={403: {"description": "Operation forbidden"}})
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(status_code=403, detail="You can only update the item: plumbus")
    return {"item_id": item_id, "name": "The great Plumbus"}
