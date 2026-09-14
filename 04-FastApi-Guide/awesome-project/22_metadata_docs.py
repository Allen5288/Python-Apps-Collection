"""
22 - Metadata and Docs URLs: title, version, description, contact, license,
     tag descriptions, and where /docs, /redoc, /openapi.json live.

Run:   fastapi dev 22_metadata_docs.py
Open:  http://127.0.0.1:8000/api/docs        (Swagger UI, moved from /docs)
       http://127.0.0.1:8000/api/redoc       (ReDoc)
       http://127.0.0.1:8000/api/openapi.json

To DISABLE a docs UI, pass None:  FastAPI(redoc_url=None)  or  docs_url=None.
To disable ALL of them (e.g. in production): FastAPI(openapi_url=None).
"""

from fastapi import FastAPI

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

# Tag metadata: ORDER here = order in the docs. Markdown allowed.
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(
    title="ChimichangApp",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpondio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",  # SPDX id (or use "url": "...")
    },
    openapi_tags=tags_metadata,
    # --- URLs ---
    openapi_url="/api/openapi.json",  # default "/openapi.json"
    docs_url="/api/docs",  # default "/docs"
    redoc_url="/api/redoc",  # default "/redoc"; None to disable
    # --- Swagger UI tweaks ---
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # hide the "Schemas" section at the bottom
        "docExpansion": "list",  # "none" | "list" | "full"
        "syntaxHighlight": {"theme": "obsidian"},
    },
)


@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]


# Servers list: useful when the API sits behind a proxy or has staging/prod URLs.
# Shown as a dropdown in Swagger UI.
app.servers = [
    {"url": "http://127.0.0.1:8000", "description": "Local"},
    {"url": "https://staging.example.com", "description": "Staging"},
]
