"""
13 - Dependency Injection: Depends, "class" dependencies, sub-dependencies,
     dependencies in decorators, global dependencies, dependencies with yield.

Run:   fastapi dev 13_dependencies.py

A dependency is just a callable (function) whose parameters are resolved the
SAME way as a path operation's (query, path, header, body, other dependencies...).
FastAPI calls it for you and hands you the return value.

Use dependencies for: shared query params, auth, DB sessions, per-request
resources with cleanup, permission checks, anything reused across endpoints.

Try:
    GET /items/?q=x&skip=1&limit=5
    GET /users/?q=x
    GET /paged/?offset=10
    GET /sub/?q=hello                      then  GET /sub/  with cookie last_query=abc
    GET /decorator-deps/  -H "X-Token: fake-super-secret-token" -H "X-Key: fake-super-secret-key"
    GET /db/items                          watch the console for open/close logs
    GET /db/fail                           the `finally` still runs
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException

# ---------------------------------------------------------------------------
# 0) GLOBAL dependency: runs for EVERY request in the app.
#    (Router-level: APIRouter(dependencies=[...]) -- see 18_bigger_app/)
# ---------------------------------------------------------------------------


async def log_request(user_agent: Annotated[str | None, Header()] = None):
    print(f"[global dep] request from {user_agent}")


app = FastAPI(dependencies=[Depends(log_request)])


# ---------------------------------------------------------------------------
# 1) Simple function dependency: shared query params.
#    Use `Annotated[type, Depends(fn)]` and give it a name to REUSE it.
# ---------------------------------------------------------------------------
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]


@app.get("/items/")
async def read_items(commons: CommonsDep):
    return commons


@app.get("/users/")
async def read_users(commons: CommonsDep):
    return commons


# ---------------------------------------------------------------------------
# 2) "Class" dependency -> return a typed object instead of a dict.
#    Recommended pattern: dataclass + a small factory function.
#    (Avoid `Depends()` with a class directly; a factory keeps types clean.)
# ---------------------------------------------------------------------------
@dataclass
class Paginator:
    offset: int = 0
    limit: int = 100
    q: str | None = None

    def page(self, data: list) -> list:
        data = [d for d in data if not self.q or self.q in d]
        return data[self.offset : self.offset + self.limit]


def get_paginator(offset: int = 0, limit: int = 100, q: str | None = None) -> Paginator:
    return Paginator(offset=offset, limit=limit, q=q)


PaginatorDep = Annotated[Paginator, Depends(get_paginator)]

fake_items = [f"item-{i}" for i in range(50)]


@app.get("/paged/")
async def read_paged(paginator: PaginatorDep):
    return {"offset": paginator.offset, "limit": paginator.limit, "items": paginator.page(fake_items)}


# ---------------------------------------------------------------------------
# 3) SUB-dependencies: a dependency can itself depend on others.
#    Here: if no ?q= is given, fall back to a cookie value.
#    Results are CACHED per request (same dep used twice -> called once),
#    unless you pass Depends(fn, use_cache=False).
# ---------------------------------------------------------------------------
def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str | None, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q


@app.get("/sub/")
async def read_query(query_or_default: Annotated[str | None, Depends(query_or_cookie_extractor)]):
    return {"q_or_cookie": query_or_default}


# ---------------------------------------------------------------------------
# 4) Dependencies in the DECORATOR: when you don't need the return value,
#    only the side effect (validation / raising errors).
# ---------------------------------------------------------------------------
async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key  # return value is ignored when used in `dependencies=[...]`


@app.get("/decorator-deps/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_protected():
    return [{"item": "Foo"}, {"item": "Bar"}]


# ---------------------------------------------------------------------------
# 5) Dependencies with YIELD: setup before `yield`, cleanup after.
#    Classic use: DB session. The code after yield runs even on exceptions
#    (put it in `finally`). Default scope="request": cleanup runs AFTER the
#    response is sent. scope="function": cleanup runs BEFORE sending.
# ---------------------------------------------------------------------------
class FakeDBSession:
    def __init__(self):
        print("  [db] open")

    def query(self):
        return ["row1", "row2"]

    def close(self):
        print("  [db] close")


def get_db():
    db = FakeDBSession()
    try:
        yield db  # <- injected value
    finally:
        db.close()  # runs after the response, even if the endpoint raised


DBDep = Annotated[FakeDBSession, Depends(get_db)]


@app.get("/db/items")
def read_db_items(db: DBDep):
    return db.query()


@app.get("/db/fail")
def read_db_fail(db: FakeDBSession = Depends(get_db)):  # old style, still valid
    raise HTTPException(status_code=400, detail="boom (db still closed, check console)")


# You can also CATCH exceptions in a yield dependency and convert them:
class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        # re-raise as HTTP error; otherwise the client gets a 500
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@app.get("/owner/{item_id}")
def get_item_owner(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id == "portal-gun":
        raise OwnerError(username)  # handled by the dependency's `except`
    return {"item_id": item_id, "owner": username}


# scope="function": cleanup happens before the response goes out.
def timing(scope_note: str = "function-scope"):
    import time

    start = time.perf_counter()
    try:
        yield scope_note
    finally:
        print(f"  [{scope_note}] took {(time.perf_counter() - start) * 1000:.2f} ms")


@app.get("/timed")
def timed(note: Annotated[str, Depends(timing, scope="function")]):
    return {"note": note}
