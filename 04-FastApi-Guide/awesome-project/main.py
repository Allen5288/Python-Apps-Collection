"""
Hub app: mounts EVERY numbered example under its own prefix so you can start
one server and browse all of them.

Run:   fastapi dev              (pyproject.toml -> entrypoint main:app)
Open:  http://127.0.0.1:8000/   -> index page linking to each example's /docs

    /00/docs   00_basics.py             /00/items/5
    /01/docs   01_query_validation.py   /01/items/?q=abc
    ...
    /18/docs   18_bigger_app/           /18/users/me?token=jessica
    /22/api/docs                        (22 moves its docs to /api/docs)

Each example is mounted as a SUB-APPLICATION (app.mount), not merged into one
router. That keeps every example self-contained: its own middleware (15, 16),
exception handlers (10), global dependencies (13, 18), docs settings (22) and
lifespan (17) all keep working. The trade-off is one /docs page per example
instead of a single giant one.

To run a single example on its own (no prefix), use its file directly:
    fastapi dev 14_security_jwt.py

Topic -> file map (the code lives in the numbered files, not here):
    00 root path, path params, predefined values / Enum, query params, body
    01 Query Parameters and String Validations (Query, Annotated)
    02 Path Parameters and Numeric Validations (Path)
    03 Query Parameter Models (BaseModel, Field, Literal, forbid extra)
    04 Body: multiple parameters, Field, nested models
    05 Declare request example data
    06 Cookie / Header params, cookie model, header model
    07 Response status code, fastapi.status, response models
    08 Form data, python-multipart, form model
    09 File, UploadFile
    10 Handle errors: HTTPException, custom headers, override exception handlers
    11 Path Operation Configuration, grouping the OpenAPI schema
    12 JSON compatible encoder: jsonable_encoder
    13 Dependency injection: class deps, sub deps, decorator deps, global deps, yield
    14 Security: get current user, OAuth2 password flow, Bearer JWT
    15 Middleware
    16 CORS
    17 SQL (relational) database with SQLModel
    18 Bigger applications, multiple files
    19 Stream JSON Lines
    20 Server-Sent Events (SSE)
    21 Background tasks
    22 Metadata and docs URLs
    23 Serve frontend apps with app.frontend   (best run standalone: its HTML uses absolute /assets paths)
    24 Static files
    25 Testing with pytest + HTTPX             (run: uv run pytest 25_testing -v)
    26 Debugging with uvicorn
"""

import importlib
import os
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

# `fastapi dev` sets this itself; set it here too so `uvicorn main:app` also
# tolerates a missing frontend build dir in 23_frontend.py.
os.environ.setdefault("FASTAPI_ENV", "development")

ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# 1) Discover the numbered examples.
#    NN_xxx.py           -> module "NN_xxx"
#    NN_xxx/main.py      -> module "NN_xxx.main"   (18_bigger_app, 25_testing)
#    Other NN_ folders (23_frontend_dist, 24_static) are assets, skipped.
# ---------------------------------------------------------------------------
@dataclass
class Example:
    number: str  # "00"
    name: str  # "00_basics"
    module_name: str  # "00_basics" or "18_bigger_app.main"
    app: FastAPI
    summary: str  # first line of the module docstring


def discover_examples() -> list[Example]:
    examples: list[Example] = []
    for path in sorted(ROOT.glob("[0-9][0-9]_*")):
        if path.is_file() and path.suffix == ".py":
            module_name = path.stem
        elif path.is_dir() and (path / "main.py").is_file():
            module_name = f"{path.name}.main"
        else:
            continue
        # importlib accepts names that start with a digit; a normal `import` statement would not.
        module = importlib.import_module(module_name)
        app = getattr(module, "app", None)
        if not isinstance(app, FastAPI):
            continue
        doc = (module.__doc__ or "").strip().splitlines()
        summary = doc[0].strip() if doc else ""
        examples.append(
            Example(
                number=path.name[:2],
                name=path.stem if path.is_file() else path.name,
                module_name=module_name,
                app=app,
                summary=summary,
            )
        )
    return examples


EXAMPLES = discover_examples()


# ---------------------------------------------------------------------------
# 2) Lifespan: Starlette does NOT run a mounted sub-app's lifespan, so run them
#    here (17_sql_database.py needs it to create its tables).
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        for ex in EXAMPLES:
            await stack.enter_async_context(ex.app.router.lifespan_context(ex.app))
        yield


app = FastAPI(
    title="FastAPI hands-on hub",
    lifespan=lifespan,
    docs_url=None,  # the hub has no API of its own; each example has its own /NN/docs
    redoc_url=None,
    openapi_url=None,
)


# `fastapi dev` always prints "Documentation at /docs". The hub has no docs of its
# own (see docs_url=None above), so send that URL to the index page instead of a 404.
@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/")

# ---------------------------------------------------------------------------
# 3) Mount each example at /NN. Inside the sub-app all paths stay the same
#    (e.g. /items/5), FastAPI handles the prefix via root_path, so each
#    sub-app's own /docs keeps working at /NN/docs.
# ---------------------------------------------------------------------------
for ex in EXAMPLES:
    app.mount(f"/{ex.number}", ex.app, name=ex.name)


# ---------------------------------------------------------------------------
# 4) Index page.
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    rows = []
    for ex in EXAMPLES:
        prefix = f"/{ex.number}"
        docs = f"{prefix}{ex.app.docs_url}" if ex.app.docs_url else None
        docs_link = f'<a href="{docs}">docs</a>' if docs else "<em>no docs</em>"
        rows.append(
            f"<tr><td><code>{ex.number}</code></td>"
            f"<td><code>{ex.name}</code></td>"
            f"<td>{ex.summary}</td>"
            f'<td>{docs_link} · <a href="{prefix}/">root</a></td></tr>'
        )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>FastAPI hands-on hub</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 1000px; padding: 0 1rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td, th {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #ddd; vertical-align: top; }}
  code {{ background: #f2f2f2; padding: 1px 4px; border-radius: 3px; }}
</style></head>
<body>
<h1>FastAPI hands-on hub</h1>
<p>Each example is mounted under its own prefix. Open its <b>docs</b> to try the endpoints.
Run one standalone with <code>fastapi dev NN_name.py</code>.</p>
<table>
<tr><th>#</th><th>file</th><th>topic</th><th>links</th></tr>
{"".join(rows)}
</table>
</body></html>"""
