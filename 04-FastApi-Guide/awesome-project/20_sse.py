"""
20 - Server-Sent Events (SSE): one-way push from server to browser over plain HTTP.

Run:   fastapi dev 20_sse.py    then open http://127.0.0.1:8000/  in a browser

SSE vs WebSocket: SSE is simpler (plain GET, auto-reconnect built into the
browser's EventSource), but server->client only. Great for progress, notifications,
LLM token streaming.

Wire format (Content-Type: text/event-stream):
    event: progress
    id: 2
    data: {"progress": 50}
    <blank line>

How in FastAPI:
    response_class=EventSourceResponse   +   yield objects
    - yield a plain object / Pydantic model  -> `data: <json>`
    - yield ServerSentEvent(...)             -> control event / id / retry / comment
    - raw_data="..."                         -> string sent as-is (no JSON quoting)

Try:
    curl -N http://127.0.0.1:8000/items/stream
    curl -N http://127.0.0.1:8000/events
    curl -N "http://127.0.0.1:8000/events" -H "Last-Event-ID: 3"   -> resumes after id 3
"""

from collections.abc import AsyncIterable
from typing import Annotated

import anyio
from fastapi import FastAPI, Header
from fastapi.responses import HTMLResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


# ---------------------------------------------------------------------------
# 1) Simplest: yield models. Each becomes `data: {...}` on the generic "message" event.
# ---------------------------------------------------------------------------
@app.get("/items/stream", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[Item]:
    yield Item(name="Plumbus", price=32.99)
    await anyio.sleep(1)
    yield Item(name="Portal Gun", price=999.99)


# ---------------------------------------------------------------------------
# 2) Full control with ServerSentEvent: named events, ids, retry, comments.
#    `Last-Event-ID` header: the browser sends it on reconnect so you can resume.
# ---------------------------------------------------------------------------
@app.get("/events", response_class=EventSourceResponse)
async def stream_events(
    last_event_id: Annotated[str | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    start = int(last_event_id) + 1 if last_event_id else 0

    # tell the client how long to wait before reconnecting (ms)
    yield ServerSentEvent(retry=3000, comment="stream started")

    for i in range(start, 6):
        yield ServerSentEvent(
            data={"progress": i * 20},  # JSON-encoded
            event="progress",  # -> addEventListener("progress", ...)
            id=str(i),  # -> Last-Event-ID on reconnect
        )
        await anyio.sleep(0.7)

    # raw string, no JSON quoting:
    yield ServerSentEvent(raw_data="all done", event="done")


# ---------------------------------------------------------------------------
# 3) Keep-alive: proxies drop idle connections; send a comment every N seconds.
#    (Comments are ignored by EventSource clients.)
# ---------------------------------------------------------------------------
@app.get("/heartbeat", response_class=EventSourceResponse)
async def heartbeat() -> AsyncIterable[ServerSentEvent]:
    for tick in range(10):
        if tick % 3 == 0:
            yield ServerSentEvent(data={"tick": tick}, event="tick")
        else:
            yield ServerSentEvent(comment="keep-alive")
        await anyio.sleep(1)


# ---------------------------------------------------------------------------
# 4) Browser client. EventSource handles reconnects + Last-Event-ID for you.
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<h3>SSE demo</h3>
<button onclick="start()">Start /events</button>
<pre id="log"></pre>
<script>
function start() {
  const log = document.getElementById('log');
  const es = new EventSource('/events');
  es.addEventListener('progress', e => log.textContent += 'progress ' + e.lastEventId + ': ' + e.data + '\\n');
  es.addEventListener('done', e => { log.textContent += 'done: ' + e.data + '\\n'; es.close(); });
  es.onerror = () => log.textContent += '(reconnecting...)\\n';
}
</script>
"""
