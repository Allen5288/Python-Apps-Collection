"""
25 - Testing with pytest + TestClient (built on HTTPX).

Run:   uv run pytest 25_testing -v

`TestClient(app)` talks to the app IN-PROCESS: no server, no network, fast.
Its API is the same as `httpx.Client` / `requests`:
    client.get(url, params=..., headers=..., cookies=...)
    client.post(url, json=..., data=..., files=...)
    response.status_code, response.json(), response.headers, response.text

Test functions are plain `def` (not async), even if the endpoints are async.
For testing async code that needs the event loop directly, use `httpx.AsyncClient`
with `ASGITransport` + `pytest-anyio` (see the last test, marked skip unless installed).

Note: pytest adds this folder to sys.path (no __init__.py here), so `from main import app` works.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, fake_db, fake_secret_token

client = TestClient(app)


# ---------------------------------------------------------------------------
# Basic
# ---------------------------------------------------------------------------
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


# ---------------------------------------------------------------------------
# Headers, 200 / 400 / 404
# ---------------------------------------------------------------------------
def test_read_item():
    response = client.get("/items/foo", headers={"X-Token": fake_secret_token})
    assert response.status_code == 200
    assert response.json() == {"id": "foo", "title": "Foo", "description": "There goes my hero"}


def test_read_item_bad_token():
    response = client.get("/items/foo", headers={"X-Token": "hailhydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_read_nonexistent_item():
    response = client.get("/items/baz", headers={"X-Token": fake_secret_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_missing_header_is_422():
    # Missing required header -> FastAPI validation error, not our 400
    response = client.get("/items/foo")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST with JSON body
# ---------------------------------------------------------------------------
def test_create_item():
    response = client.post(
        "/items/",
        headers={"X-Token": fake_secret_token},
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"}
    assert "foobar" in fake_db  # side effect happened


def test_create_existing_item():
    response = client.post(
        "/items/",
        headers={"X-Token": fake_secret_token},
        json={"id": "foo", "title": "The Foo ID Stealers", "description": "x"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Item already exists"}


def test_create_item_invalid_body():
    response = client.post("/items/", headers={"X-Token": fake_secret_token}, json={"title": "no id"})
    assert response.status_code == 422
    # error list tells you exactly which field failed
    assert response.json()["detail"][0]["loc"] == ["body", "id"]


# ---------------------------------------------------------------------------
# Parametrize: one test, many inputs
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("item_id", "expected_status"),
    [("foo", 200), ("bar", 200), ("nope", 404)],
)
def test_read_items_parametrized(item_id: str, expected_status: int):
    response = client.get(f"/items/{item_id}", headers={"X-Token": fake_secret_token})
    assert response.status_code == expected_status


# ---------------------------------------------------------------------------
# Fixture: a pre-authenticated client so tests don't repeat the header.
# ---------------------------------------------------------------------------
@pytest.fixture
def auth_client():
    with TestClient(app, headers={"X-Token": fake_secret_token}) as c:
        # `with` also runs the app's lifespan/startup events (none here, but good habit)
        yield c


def test_with_fixture(auth_client: TestClient):
    assert auth_client.get("/items/bar").status_code == 200


# ---------------------------------------------------------------------------
# Overriding a dependency in tests (pattern shown on a tiny inline app).
# `app.dependency_overrides[original] = replacement` swaps ANY dependency,
# e.g. a real DB session for an in-memory one, or `get_current_user` for a fake.
# ---------------------------------------------------------------------------
from typing import Annotated  # noqa: E402

from fastapi import Depends, FastAPI  # noqa: E402


def get_current_user():
    raise RuntimeError("would hit a real auth system")


mini_app = FastAPI()


@mini_app.get("/me")
def me(user: Annotated[str, Depends(get_current_user)]):
    return {"user": user}


def test_dependency_override():
    mini_app.dependency_overrides[get_current_user] = lambda: "test-user"
    try:
        r = TestClient(mini_app).get("/me")
        assert r.json() == {"user": "test-user"}
    finally:
        mini_app.dependency_overrides.clear()  # always clean up


# ---------------------------------------------------------------------------
# Async test with httpx.AsyncClient (needs `pytest-anyio` or `anyio` plugin:
#   uv add --dev anyio ; pytest picks up the `anyio` marker automatically).
# ---------------------------------------------------------------------------
import httpx  # noqa: E402

anyio_available = pytest.importorskip("anyio", reason="anyio pytest plugin not installed")


@pytest.mark.anyio
async def test_async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
