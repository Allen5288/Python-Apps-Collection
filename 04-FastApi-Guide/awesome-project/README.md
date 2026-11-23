# FastAPI hands-on examples

One runnable file per topic, in learning order. Every file starts with a docstring that
says what the topic is, how to run it, and which URLs / curl commands to try.
Code comments explain each line that matters.

```bash
uv sync                          # install deps (fastapi[standard], pyjwt, pwdlib, sqlmodel, pytest)

fastapi dev                      # ALL examples at once (main.py hub) -> http://127.0.0.1:8000/
                                 #   each example lives under its number: /00/docs, /01/docs, ... /26/docs

fastapi dev 00_basics.py         # or ONE example on its own -> http://127.0.0.1:8000/docs
fastapi dev 18_bigger_app/main.py
uv run pytest 25_testing -v
uv run python 26_debugging.py
```

`main.py` mounts every numbered example as a sub-application under `/NN`, so one server
serves all of them and each keeps its own middleware, error handlers, and docs page.
The index page at `/` links to every example's docs.

| # | File | Topic |
|---|------|-------|
| 00 | `00_basics.py` | App, path params, route order, Enum, query params, request body |
| 01 | `01_query_validation.py` | `Query()` + `Annotated`: min/max length, pattern, lists, alias, deprecated, AfterValidator |
| 02 | `02_path_validation.py` | `Path()`: gt / ge / lt / le, string constraints |
| 03 | `03_query_param_models.py` | Query params as a Pydantic model, `Field`, `Literal`, `extra="forbid"` |
| 04 | `04_body.py` | Multiple body params, `Body()`, `embed`, `Field`, nested models, list / dict bodies |
| 05 | `05_request_examples.py` | Example data: `model_config`, `Field(examples=)`, `Body(examples=)`, `openapi_examples` |
| 06 | `06_cookie_header.py` | `Cookie()`, `Header()`, cookie model, header model, setting cookies on the response |
| 07 | `07_response_status.py` | `status_code=`, `fastapi.status`, return types vs `response_model`, exclude_unset, dynamic status |
| 08 | `08_form_data.py` | `Form()`, form models, forbid extra fields |
| 09 | `09_files.py` | `File()` bytes, `UploadFile`, multiple files, files + form, chunked save |
| 10 | `10_error_handling.py` | `HTTPException`, error headers, custom exception classes, overriding default handlers |
| 11 | `11_path_operation_config.py` | tags, summary, description, deprecated, operation_id, `responses=`, hiding routes, tag order |
| 12 | `12_jsonable_encoder.py` | `jsonable_encoder` for datetime / UUID / Decimal / sets / models |
| 13 | `13_dependencies.py` | `Depends`, dataclass deps, sub-deps, decorator deps, global deps, `yield` deps + scope |
| 14 | `14_security_jwt.py` | OAuth2 password flow, Bearer JWT, `get_current_user`, active-user and admin checks |
| 15 | `15_middleware.py` | `@app.middleware("http")`, request id, short-circuit, `GZipMiddleware` |
| 16 | `16_cors.py` | `CORSMiddleware` options, preflight, a browser demo page |
| 17 | `17_sql_database.py` | SQLModel + SQLite: table / public / create / update models, session dep, CRUD, lifespan |
| 18 | `18_bigger_app/` | `APIRouter` in multiple files, router-level prefix/tags/deps, `include_router` options |
| 19 | `19_stream_json_lines.py` | Stream JSON Lines with `AsyncIterable[Model]` and `yield` |
| 20 | `20_sse.py` | Server-Sent Events: `EventSourceResponse`, `ServerSentEvent`, ids, retry, browser client |
| 21 | `21_background_tasks.py` | `BackgroundTasks` from endpoints and dependencies, sync vs async tasks |
| 22 | `22_metadata_docs.py` | Title / version / contact / license, tag metadata, moving `/docs` `/redoc` `/openapi.json` |
| 23 | `23_frontend.py` | Serve a built SPA with `app.frontend()` and `router.frontend()` |
| 24 | `24_static_files.py` | `StaticFiles` mount, `url_for`, `FileResponse` downloads |
| 25 | `25_testing/` | pytest + `TestClient`: headers, JSON, parametrize, fixtures, `dependency_overrides`, async client |
| 26 | `26_debugging.py` | `uvicorn.run` under `__main__`, VS Code / PyCharm launch configs, logging |
| 28 | `28_websockets.py` | WebSockets: rooms, broadcast, `ConnectionManager`, disconnect cleanup, `TestClient` websocket test |


Generated at runtime and ignored by git: `database.db` (17), `log.txt` (21), `.uploads/` (09).
