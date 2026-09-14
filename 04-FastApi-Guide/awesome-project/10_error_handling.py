"""
10 - Error handling: HTTPException, custom headers, custom exceptions,
     overriding the default handlers (validation errors, HTTPException).

Run:   fastapi dev 10_error_handling.py

Try:
    GET /items/foo                 -> 200
    GET /items/bar                 -> 404 {"detail": "Item not found"}
    GET /items-header/bar          -> 404 + response header X-Error
    GET /unicorns/yolo             -> 418 from a CUSTOM exception class + handler
    GET /validated/abc             -> 422, but with a PLAIN TEXT body (overridden handler)
    GET /validated/3               -> 418 via HTTPException, plain text (overridden handler)
    POST /items/ {"title":"x","size":"no"} -> 422 with the ORIGINAL body echoed back
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


# ---------------------------------------------------------------------------
# 1) HTTPException: RAISE it (don't return it). Execution stops immediately,
#    even deep inside helper functions/dependencies. `detail` can be any JSON.
# ---------------------------------------------------------------------------
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"item": items[item_id]}


# ---------------------------------------------------------------------------
# 2) Custom headers on the error response (e.g. WWW-Authenticate for 401).
# ---------------------------------------------------------------------------
@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail={"msg": "Item not found", "item_id": item_id},  # detail can be a dict
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


# ---------------------------------------------------------------------------
# 3) CUSTOM exception class + @app.exception_handler.
#    Your domain code raises `UnicornException`; FastAPI turns it into a response.
# ---------------------------------------------------------------------------
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


# ---------------------------------------------------------------------------
# 4) OVERRIDE the default handlers.
#    - RequestValidationError : what FastAPI raises on 422 (bad input)
#    - StarletteHTTPException : the base class of FastAPI's HTTPException.
#      Register the handler for the *Starlette* one so it also catches errors
#      raised by Starlette internals (e.g. 404 for unknown routes).
# ---------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"OMG! An HTTP error!: {exc!r}")  # e.g. log it
    # Option A: fully custom response
    # return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
    # Option B: do something, then REUSE the default handler
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"OMG! The client sent invalid data!: {exc}")
    # Reuse the default (returns the standard {"detail": [...]} JSON):
    # return await request_validation_exception_handler(request, exc)
    # Or return plain text:
    return PlainTextResponse(str(exc), status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


@app.get("/validated/{item_id}")
async def read_validated(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}


# ---------------------------------------------------------------------------
# 5) Access the invalid body in a validation error: `exc.body`.
#    Useful for debugging clients. (This handler REPLACES the one above, since
#    only one handler per exception type is kept — last registration wins.)
# ---------------------------------------------------------------------------
class Item(BaseModel):
    title: str
    size: int


@app.exception_handler(RequestValidationError)
async def validation_exception_handler_with_body(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post("/items/")
async def create_item(item: Item):
    return item


# ---------------------------------------------------------------------------
# 6) Catch-all for unexpected exceptions -> 500 with a stable JSON shape.
#    (In dev, uvicorn still prints the traceback to the console.)
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/boom")
async def boom():
    raise RuntimeError("something unexpected")


# silence unused-import warning for the reference example in the comments above
_ = request_validation_exception_handler
