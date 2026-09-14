"""
16 - CORS (Cross-Origin Resource Sharing).

Run:   fastapi dev 16_cors.py
Then open  http://127.0.0.1:8000/demo  in the browser: the page is served from
127.0.0.1:8000 and calls  http://localhost:8000/api  -> a DIFFERENT origin
(host differs), so the browser enforces CORS.

An "origin" = scheme + host + port.   http://localhost:8080 != http://localhost:3000

The browser (not curl!) blocks JS on origin A from reading responses of origin B
unless B replies with `Access-Control-Allow-Origin` headers. CORSMiddleware adds them.
For non-simple requests the browser first sends an OPTIONS "preflight" request;
the middleware answers it automatically.

Rules:
    allow_origins=["*"]  is NOT allowed together with allow_credentials=True
    (cookies / Authorization). List explicit origins in that case, or use allow_origin_regex.

Try with curl (simulating a browser):
    curl -i http://127.0.0.1:8000/api -H "Origin: http://localhost:3000"       -> has Access-Control-Allow-Origin
    curl -i http://127.0.0.1:8000/api -H "Origin: http://evil.com"             -> no CORS headers
    curl -i -X OPTIONS http://127.0.0.1:8000/api \
        -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST"  -> preflight 200
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# Frontends allowed to call this API. Typical dev setup: Vite/React on 5173/3000.
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",  # used by the /demo page below
    "https://myapp.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # exact list; or ["*"] for a public API without credentials
    # allow_origin_regex=r"https://.*\.example\.com",  # alternative: pattern
    allow_credentials=True,  # allow cookies / Authorization header
    allow_methods=["*"],  # default is only ["GET"]
    allow_headers=["*"],  # default is []. Needed for e.g. Authorization, Content-Type: application/json
    expose_headers=["X-Request-ID"],  # response headers JS is allowed to read (besides the safe ones)
    max_age=600,  # seconds browsers may cache the preflight result
)


@app.get("/api")
async def api():
    return {"message": "Hello from the API"}


@app.post("/api")
async def api_post(payload: dict):
    return {"received": payload}


# A tiny page to see CORS working (and failing) in a real browser.
# The page's origin is http://127.0.0.1:8000. It calls http://localhost:8000/api,
# a different origin. Since "http://127.0.0.1:8000" is NOT in `origins`, the
# browser blocks it. Add it to the list, reload, and the call succeeds.
@app.get("/demo", response_class=HTMLResponse)
async def demo():
    return """
<h3>CORS demo</h3>
<p>This page is served from <code>http://127.0.0.1:8000</code> and will call
<code>http://localhost:8000/api</code> (different origin). Open DevTools &gt; Console.</p>
<button onclick="call()">POST http://localhost:8000/api</button>
<pre id="out"></pre>
<script>
async function call() {
  const out = document.getElementById('out');
  try {
    const r = await fetch('http://localhost:8000/api', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({a: 1}),
    });
    out.textContent = JSON.stringify(await r.json(), null, 2);
  } catch (e) {
    out.textContent = 'Blocked by CORS (see console): ' + e;
  }
}
</script>
<p>Expected: blocked. Fix: add <code>"http://127.0.0.1:8000"</code> to <code>origins</code> in 16_cors.py.</p>
"""
