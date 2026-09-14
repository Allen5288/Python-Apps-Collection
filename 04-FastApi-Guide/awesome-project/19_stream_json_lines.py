"""
19 - Stream JSON Lines (NDJSON): one JSON object per line, sent as they are produced.

Run:   fastapi dev 19_stream_json_lines.py

How: declare the return type as `AsyncIterable[Model]` (or `Iterable[Model]`)
and `yield` objects. FastAPI streams each one as a JSON line
(Content-Type: application/jsonl). Client reads line by line, no need to wait
for the whole response. Good for large exports / LLM-style token streams.

Try:
    curl -N http://127.0.0.1:8000/items/stream        (-N = no buffering, see lines arrive)
    curl -N http://127.0.0.1:8000/numbers/stream?n=5
    curl -N http://127.0.0.1:8000/logs/stream          (sync generator version)
"""

from collections.abc import AsyncIterable, Iterable

import anyio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


items = [
    Item(name="Plumbus", price=32.99),
    Item(name="Portal Gun", price=999.99),
    Item(name="Meeseeks Box", price=49.5),
]


# ---------------------------------------------------------------------------
# 1) Async generator + return type -> JSON Lines automatically.
#    Each yielded Item is validated/serialized by Pydantic and sent as one line.
# ---------------------------------------------------------------------------
@app.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item
        await anyio.sleep(0.5)  # simulate slow production; use `curl -N` to see it


# ---------------------------------------------------------------------------
# 2) Streaming plain types works too (dicts, ints...). Query params still work.
# ---------------------------------------------------------------------------
@app.get("/numbers/stream")
async def stream_numbers(n: int = 10) -> AsyncIterable[dict]:
    for i in range(n):
        yield {"i": i, "square": i * i}
        await anyio.sleep(0.2)


# ---------------------------------------------------------------------------
# 3) Sync generator (`def` + `yield`): fine when the source is blocking code.
#    FastAPI runs it in a threadpool so the event loop isn't blocked.
# ---------------------------------------------------------------------------
class LogLine(BaseModel):
    level: str
    msg: str


@app.get("/logs/stream")
def stream_logs() -> Iterable[LogLine]:
    import time

    for i in range(5):
        yield LogLine(level="INFO", msg=f"line {i}")
        time.sleep(0.3)  # blocking is OK here because it's a sync function


# ---------------------------------------------------------------------------
# 4) How a CLIENT consumes it (Python + httpx). Save as a separate script:
#
#   import httpx, json
#   with httpx.stream("GET", "http://127.0.0.1:8000/items/stream") as r:
#       for line in r.iter_lines():
#           if line:
#               print(json.loads(line))
# ---------------------------------------------------------------------------
