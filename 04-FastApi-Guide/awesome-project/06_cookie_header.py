"""
06 - Cookie and Header parameters (+ Cookie models and Header models).

Run:   fastapi dev 06_cookie_header.py

`Cookie()` and `Header()` work exactly like `Query()`, they just read from a
different place. You MUST use them explicitly, otherwise the param is a query.

Header gotchas:
    - HTTP headers use hyphens: `User-Agent`. Python can't: `user_agent`.
      FastAPI converts underscores -> hyphens automatically (convert_underscores=True).
    - Headers are case-insensitive.
    - Duplicate headers -> declare as `list[str]`.

Try with curl:
    curl http://127.0.0.1:8000/items/ -H "X-Token: abc" -b "ads_id=123;session_id=xyz"
    curl http://127.0.0.1:8000/headers/list -H "X-Token: a" -H "X-Token: b"
    curl http://127.0.0.1:8000/headers/model -H "Host: x" -H "save-data: on" -H "x-tag: a" -H "x-tag: b"
    curl http://127.0.0.1:8000/cookies/model -b "session_id=abc;fatebook_tracker=x;googall_tracker=y"
    curl http://127.0.0.1:8000/cookies/strict -b "session_id=abc;evil=1"     -> 422 (extra forbid)
"""

from typing import Annotated

from fastapi import Cookie, FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Individual cookie + header values.
# ---------------------------------------------------------------------------
@app.get("/items/")
async def read_items(
    ads_id: Annotated[str | None, Cookie()] = None,
    session_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,  # reads "User-Agent"
    x_token: Annotated[str | None, Header()] = None,  # reads "X-Token"
):
    return {"ads_id": ads_id, "session_id": session_id, "user_agent": user_agent, "x_token": x_token}


# ---------------------------------------------------------------------------
# 2) Disable the underscore -> hyphen conversion if the header really has
#    an underscore (rare; many proxies drop such headers).
# ---------------------------------------------------------------------------
@app.get("/headers/raw-underscore")
async def read_raw_header(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    return {"strange_header": strange_header}


# ---------------------------------------------------------------------------
# 3) Duplicate headers -> list.   -H "X-Token: a" -H "X-Token: b"  => ["a","b"]
# ---------------------------------------------------------------------------
@app.get("/headers/list")
async def read_header_list(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}


# ---------------------------------------------------------------------------
# 4) HEADER MODEL: group related headers in a Pydantic model.
# ---------------------------------------------------------------------------
class CommonHeaders(BaseModel):
    host: str
    save_data: bool  # header "save-data"
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []  # repeated header


@app.get("/headers/model")
async def read_headers_model(headers: Annotated[CommonHeaders, Header()]):
    return headers


# forbid unexpected headers - careful: browsers send many headers, so this is
# mostly useful for machine-to-machine APIs.
class StrictHeaders(BaseModel):
    model_config = {"extra": "forbid"}
    x_api_key: str


# ---------------------------------------------------------------------------
# 5) COOKIE MODEL: same idea for cookies.
# ---------------------------------------------------------------------------
class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/cookies/model")
async def read_cookies_model(cookies: Annotated[Cookies, Cookie()]):
    return cookies


class StrictCookies(BaseModel):
    model_config = {"extra": "forbid"}  # any other cookie -> 422
    session_id: str


@app.get("/cookies/strict")
async def read_cookies_strict(cookies: Annotated[StrictCookies, Cookie()]):
    return cookies


# ---------------------------------------------------------------------------
# 6) SETTING a cookie / header on the response: use the `Response` param.
#    Declare `response: Response` and FastAPI injects a response object whose
#    headers/cookies are merged into the final response.
# ---------------------------------------------------------------------------
from fastapi import Response  # noqa: E402


@app.post("/cookies/set")
async def set_cookie(response: Response):
    response.set_cookie(key="session_id", value="fake-session-value", httponly=True, max_age=3600)
    response.headers["X-Custom-Header"] = "hello"
    return {"message": "cookie + header set"}
