"""30 - Dependency caching: when FastAPI reuses a dependency, and when to stop it.

Topic: Depends() caches its result *per request* by default. Call
the same dependency twice in one request — directly, or through
two sub-dependencies — and the function runs once; both callers
get the same return value. That is usually what you want (one DB
session per request, one auth check per request). It bites when
the dependency is supposed to produce a *fresh* value every time
it is called — a new id, a timestamp, a counter.

The switch is `use_cache=False` on Depends(). It is per-use, not
per-dependency: the same function can be cached in one endpoint
and fresh in another. This example shows both, so the difference
is visible in the response instead of argued about in a comment.

Run:
    fastapi dev 30_dependency_caching.py   # -> http://127.0.0.1:8000/docs

Try:
    curl http://127.0.0.1:8000/ids          # same id twice (cached)
    curl http://127.0.0.1:8000/ids-fresh    # two different ids
    curl http://127.0.0.1:8000/session      # one session id, shared by two sub-deps

Daily note, 2026-11-27: caching is per request, not per app — a
new request re-runs the dependency. The gotcha is only *within*
one request, which is exactly where it is hardest to notice.
"""

import uuid

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="30 - Dependency caching")


def new_request_id() -> str:
    """A fresh value every time it runs. Used twice in one endpoint
    below, so the cached and the fresh behaviour are side by side."""
    return str(uuid.uuid4())


def get_db_session() -> dict:
    """Stands in for a real session (SQLModel Session, a connection
    from a pool). Opening it is the expensive part, so sharing one
    per request is the point — two sub-dependencies that each need
    the session must get the *same* one, not two."""
    return {"session_id": str(uuid.uuid4()), "open": True}


def sub_dependency_a(session: dict = Depends(get_db_session)) -> str:
    return session["session_id"]


def sub_dependency_b(session: dict = Depends(get_db_session)) -> str:
    return session["session_id"]


@app.get("/ids")
def cached_ids(first: str = Depends(new_request_id),
               second: str = Depends(new_request_id)):
    """Both parameters call the same dependency. FastAPI runs it
    once per request and hands the same value to both — so first
    and second are EQUAL. Surprising the first time you see it,
    and the reason a "generate a new id" dependency must never be
    shared this way."""
    return {"first": first, "second": second, "same": first == second}


@app.get("/ids-fresh")
def fresh_ids(first: str = Depends(new_request_id, use_cache=False),
              second: str = Depends(new_request_id, use_cache=False)):
    """Same dependency, caching off per use. The function runs twice
    and the two ids differ. This is the correct shape for anything
    that must be fresh per call — a new id, a timestamp taken at
    the point of use, a counter increment."""
    return {"first": first, "second": second, "same": first == second}


@app.get("/session")
def shared_session(a: str = Depends(sub_dependency_a),
                   b: str = Depends(sub_dependency_b)):
    """Two sub-dependencies each depend on get_db_session. The
    cache is what makes them share one session: the function runs
    once, both sub-deps get the same session id. Turn the cache off
    here and each sub-dep would open its own session — two
    connections, two transactions, and a write in one invisible
    to a read in the other."""
    return {"sub_a_session": a, "sub_b_session": b, "shared": a == b}


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Rules to remember (run with: uv run pytest 30_dependency_caching.py -v
# only if you add tests — the snippet below is the pattern to copy):
#
#     from fastapi.testclient import TestClient
#
#     def test_cached_dependency_returns_same_value():
#         with TestClient(app) as client:
#             assert client.get("/ids").json()["same"] is True
#
#     def test_fresh_dependency_returns_different_values():
#         with TestClient(app) as client:
#             assert client.get("/ids-fresh").json()["same"] is False
#
#     def test_sub_dependencies_share_one_session():
#         with TestClient(app) as client:
#             assert client.get("/session").json()["shared"] is True
#
# - Cache ON (default): one run per request. Right for sessions,
#   auth checks, loaded config — anything expensive or that must be
#   the same object for the whole request.
# - Cache OFF (use_cache=False): one run per use. Right for fresh
#   values — ids, timestamps, counters — and for dependencies with
#   side effects you need to happen twice.
# - The cache key is the dependency function, not the parameter
#   name: two parameters calling the same function share one run.
#   Two different functions that happen to do the same thing do not.
# - Yield dependencies (see 13) are cached the same way — and the
#   cleanup after `yield` still runs once, at the end of the
#   request, not once per use. Do not turn the cache off on a yield
#   dependency that opens a connection unless you want two
#   connections and two cleanups.
# ---------------------------------------------------------------------------
