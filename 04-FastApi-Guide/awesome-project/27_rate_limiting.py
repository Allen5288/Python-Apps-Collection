"""27 - Rate limiting with a token bucket (no extra dependency).

Topic: protect a FastAPI endpoint from abuse / accidental floods.
This file is the next numbered example in the FastAPI guide
(00-26 already exist) — run it on its own, or mount it in main.py
like the other examples.

Run:
    fastapi dev 27_rate_limiting.py        # -> http://127.0.0.1:8000/docs
    # or: uvicorn 27_rate_limiting:app --reload

Try:
    curl http://127.0.0.1:8000/limited     # 5 requests per 10s per client
    curl http://127.0.0.1:8000/health      # never rate-limited
    # 6th quick call to /limited returns 429 with Retry-After

Daily note, 2026-11-20: this is day 1 of the rate-limiting topic.
Next days in this same file: per-user limits (after auth, see
14_security_jwt.py), and a Redis-backed limiter for multiple
servers — the in-memory bucket here is correct for one process
only, and that limitation is called out below.
"""

import time
from collections import defaultdict

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="27 - Rate limiting")


class TokenBucket:
    """Simple token bucket: capacity tokens, refilled at rate/sec."""

    def __init__(self, capacity: int, refill_per_second: float) -> None:
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.tokens = float(capacity)
        self.updated_at = time.monotonic()

    def allow(self) -> tuple[bool, float]:
        now = time.monotonic()
        elapsed = now - self.updated_at
        self.updated_at = now
        # Refill, but never above capacity.
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        if self.tokens >= 1:
            self.tokens -= 1
            return True, 0.0
        # Not enough tokens: how long until the next one?
        wait = (1 - self.tokens) / self.refill_per_second
        return False, wait


# One bucket per client IP. In-memory only: each worker process
# has its own buckets, so use Redis (or a gateway) when you run
# more than one process / server.
_BUCKETS: dict[str, TokenBucket] = defaultdict(lambda: TokenBucket(capacity=5, refill_per_second=0.5))


def rate_limit(request: Request) -> None:
    """Dependency: 5 requests per 10 seconds per client IP.

    Raises a 429 as a JSONResponse with Retry-After, instead of
    letting the handler run.
    """
    client = request.client.host if request.client else "unknown"
    allowed, wait = _BUCKETS[client].allow()
    if not allowed:
        # FastAPI dependencies cannot return a response directly,
        # so raise an exception the handler below turns into 429.
        raise RateLimited(retry_after=wait)


class RateLimited(Exception):
    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after


@app.exception_handler(RateLimited)
async def rate_limited_handler(request: Request, exc: RateLimited) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests — slow down."},
        headers={"Retry-After": str(int(exc.retry_after) + 1)},
    )


@app.get("/limited", dependencies=[Depends(rate_limit)])
def limited() -> dict[str, str]:
    return {"message": "OK — you are within the limit."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
