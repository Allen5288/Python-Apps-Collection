"""
08 - Form data (`Form()`), Form models.

Run:   fastapi dev 08_form_data.py

Requires `python-multipart` (already in fastapi[standard]).
Forms arrive as `application/x-www-form-urlencoded` (or multipart when files
are involved), NOT JSON. You cannot mix `Form()` params and JSON body params
in one endpoint: the HTTP request has only one body encoding.

Try:
    curl -X POST http://127.0.0.1:8000/login/ -d "username=allen&password=secret"
    curl -X POST http://127.0.0.1:8000/login/model -d "username=allen&password=secret"
    curl -X POST http://127.0.0.1:8000/login/strict -d "username=allen&password=secret&extra=1"  -> 422
    Or use /docs: Swagger UI renders a form for you.
"""

from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Individual form fields.  (OAuth2 "password flow" requires exactly this shape:
#    form fields named `username` and `password`.)
# ---------------------------------------------------------------------------
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}  # never return the password


# ---------------------------------------------------------------------------
# 2) Form MODEL: group fields in a Pydantic model, annotate the param with Form().
# ---------------------------------------------------------------------------
class FormData(BaseModel):
    username: str
    password: str
    remember_me: bool = False  # checkbox: "on"/"true"/"1" -> True


@app.post("/login/model")
async def login_model(data: Annotated[FormData, Form()]):
    return {"username": data.username, "remember_me": data.remember_me}


# ---------------------------------------------------------------------------
# 3) Forbid extra form fields with model_config.
# ---------------------------------------------------------------------------
class StrictFormData(BaseModel):
    model_config = {"extra": "forbid"}
    username: str
    password: str


@app.post("/login/strict")
async def login_strict(data: Annotated[StrictFormData, Form()]):
    return {"username": data.username}


# ---------------------------------------------------------------------------
# 4) Optional + validated form fields (Form() takes the same args as Query()).
# ---------------------------------------------------------------------------
@app.post("/profile/")
async def update_profile(
    display_name: Annotated[str, Form(min_length=2, max_length=30)],
    bio: Annotated[str | None, Form(max_length=200)] = None,
    age: Annotated[int | None, Form(ge=0, le=150)] = None,
):
    return {"display_name": display_name, "bio": bio, "age": age}
