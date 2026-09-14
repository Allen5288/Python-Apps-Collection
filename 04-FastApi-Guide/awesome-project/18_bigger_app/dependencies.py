"""Shared dependencies used by several routers."""

from typing import Annotated

from fastapi import Header, HTTPException


async def get_token_header(x_token: Annotated[str, Header()]):
    """Header-based check. Used by the items router and the admin router."""
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    """Query-based check. Used as a GLOBAL dependency in main.py."""
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")
