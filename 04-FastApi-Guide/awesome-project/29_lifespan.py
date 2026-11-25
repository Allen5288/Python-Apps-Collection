"""29 - Lifespan events: startup and shutdown, done properly.

Topic: run code when the app starts (load a model, open a
connection pool, warm a cache) and when it stops (close the pool,
flush the logs), with FastAPI's lifespan handler.

The old way — `@app.on_event("startup")` / `"shutdown"` — is
deprecated. The current way is a single `@asynccontextmanager`
function passed as `lifespan=` to FastAPI: everything before the
`yield` runs at startup, everything after it runs at shutdown,
and an exception before the `yield` stops the app from starting
at all (which is what you want — a half-started app is worse
than a crashed one).

This example loads a tiny in-memory catalogue at startup (standing
in for a model file, a DB pool, or an index), serves it from
`request.state`, and proves the shutdown step ran by writing a
marker file.

Run:
    fastapi dev 29_lifespan.py        # -> http://127.0.0.1:8000/docs
    # or: uvicorn 29_lifespan:app --reload

Try:
    curl http://127.0.0.1:8000/catalogue
    curl http://127.0.0.1:8000/catalogue/kiwi
    curl http://127.0.0.1:8000/health     # 200 only after startup finished
    # stop the server (Ctrl+C), then: cat shutdown.log

Daily note, 2026-11-26: this is day 1 of the lifespan topic.
Next days in this same file: sharing one lifespan across several
mounted apps (the hub in main.py runs each sub-app's lifespan —
see its AsyncExitStack), and testing lifespan with TestClient.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

HERE = Path(__file__).parent
SHUTDOWN_LOG = HERE / "shutdown.log"


def load_catalogue() -> dict[str, dict]:
    """Startup work: load the resource the app needs to serve.

    In a real app this is where you load the ML model, create the
    DB connection pool, or build the search index — once, at boot,
    not once per request. It is deliberately slow-ish (a file read)
    so a failure here is visible at startup, not on the first
    user request.
    """
    catalogue = {
        "kiwi": {"name": "Kiwi", "price_aud": 1.20, "in_stock": 140},
        "mango": {"name": "Mango", "price_aud": 2.50, "in_stock": 60},
        "fig": {"name": "Fig", "price_aud": 3.10, "in_stock": 0},
    }
    if not catalogue:
        # Fail fast: raising here stops the app starting. A server
        # that starts without its catalogue would answer every
        # request with a 500 — worse than not starting at all.
        raise RuntimeError("catalogue is empty — refusing to start")
    return catalogue


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup (before yield) ----
    catalogue = load_catalogue()
    app.state.catalogue = catalogue
    app.state.started = True
    print(f"lifespan: catalogue loaded ({len(catalogue)} items)")
    yield
    # ---- shutdown (after yield) ----
    # Runs even if a request is in flight — FastAPI waits for the
    # shutdown code before the process exits. Close pools, flush
    # buffers, and write anything the next start needs to know.
    app.state.started = False
    SHUTDOWN_LOG.write_text("shutdown ran — catalogue closed cleanly\n")
    print("lifespan: shutdown complete")


app = FastAPI(title="29 - Lifespan events", lifespan=lifespan)


@app.get("/health")
async def health(request: Request):
    """200 only once startup has finished — a load balancer can
    use this to know the app is really ready, not just listening."""
    ready = getattr(request.app.state, "started", False)
    return JSONResponse(
        {"status": "ok" if ready else "starting"},
        status_code=200 if ready else 503,
    )


@app.get("/catalogue")
async def list_catalogue(request: Request):
    """The catalogue lives on app.state — loaded once at startup,
    read by every request, never reloaded per request."""
    return {"items": list(request.app.state.catalogue.values())}


@app.get("/catalogue/{item_id}")
async def get_item(item_id: str, request: Request):
    catalogue = request.app.state.catalogue
    item = catalogue.get(item_id)
    if item is None:
        return JSONResponse({"detail": f"no item {item_id!r}"}, status_code=404)
    return item


# ---------------------------------------------------------------------------
# How to test a lifespan (run with: uv run pytest 29_lifespan.py -v
# only if you add tests — the snippet below is the pattern to copy):
#
#     from fastapi.testclient import TestClient
#
#     def test_catalogue_loads_at_startup():
#         # TestClient as a context manager runs lifespan on entry
#         # and shutdown on exit — a bare TestClient(...) does NOT.
#         with TestClient(app) as client:
#             assert client.get("/catalogue").status_code == 200
#         assert SHUTDOWN_LOG.exists()  # shutdown ran on exit
#
# The common mistake: creating TestClient(app) without `with` and
# wondering why app.state has no catalogue. Lifespan only runs
# inside the context manager (or when the server actually starts).
# ---------------------------------------------------------------------------
