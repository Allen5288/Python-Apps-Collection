"""
15 - Middleware: code that runs for EVERY request before the endpoint and for
     every response after it.

Run:   fastapi dev 15_middleware.py

    request  -> [middleware 1 -> middleware 2 -> ... -> endpoint] -> response
                     ^--- can modify request / short-circuit          ^--- can modify response

Two ways:
    A) @app.middleware("http")  decorator  -> quick function-style middleware
    B) app.add_middleware(SomeMiddlewareClass, **options) -> reusable classes
       (CORSMiddleware, GZipMiddleware, TrustedHostMiddleware, HTTPSRedirectMiddleware, custom)

Order: the LAST added middleware is the OUTERMOST (runs first on the request).

Try:
    curl -i http://127.0.0.1:8000/               -> see X-Process-Time and X-Request-ID headers
    curl -i http://127.0.0.1:8000/slow
    curl -i http://127.0.0.1:8000/blocked        -> 403 short-circuited by middleware
    curl -i http://127.0.0.1:8000/big -H "Accept-Encoding: gzip" | head  -> Content-Encoding: gzip
"""

import time
import uuid

import anyio
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()


# ---------------------------------------------------------------------------
# A) Function middleware. `call_next(request)` runs the rest of the chain
#    (other middleware + the endpoint) and returns the response.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start
    # Custom headers should use the `X-` prefix (or any name; `X-` is convention)
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Request ID: generate one, store it on `request.state` so endpoints/deps can use it,
# and echo it back to the client.
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id  # available to endpoints via `request.state`
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Short-circuit: return a response WITHOUT calling the endpoint.
@app.middleware("http")
async def block_path(request: Request, call_next):
    if request.url.path == "/blocked":
        return JSONResponse(status_code=403, content={"detail": "blocked by middleware"})
    return await call_next(request)


# Simple logging middleware.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"--> {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"<-- {response.status_code}")
    return response


# ---------------------------------------------------------------------------
# B) Class-based middleware. GZip compresses responses bigger than `minimum_size`
#    bytes when the client sends Accept-Encoding: gzip.
# ---------------------------------------------------------------------------
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Other built-ins you may want (uncomment to try):
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com", "127.0.0.1", "localhost"])
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# app.add_middleware(HTTPSRedirectMiddleware)   # http:// -> https:// (production behind TLS)


# ---------------------------------------------------------------------------
# Endpoints to exercise the middleware
# ---------------------------------------------------------------------------
@app.get("/")
async def root(request: Request):
    return {"message": "Hello", "request_id": request.state.request_id}


@app.get("/slow")
async def slow():
    await anyio.sleep(0.5)  # non-blocking sleep so X-Process-Time ~0.5
    return {"message": "that was slow"}


@app.get("/blocked")
async def blocked():
    return {"message": "you will never see this"}


@app.get("/big")
async def big():
    return {"data": "x" * 5000}  # > 1000 bytes -> gzipped if client accepts it
