"""
23 - Serve a built frontend app (Vite / React / Vue / Svelte / Angular `dist/`)
     with `app.frontend()`.

Run:   fastapi dev 23_frontend.py
Open:  http://127.0.0.1:8000/          -> index.html from 23_frontend_dist/
       http://127.0.0.1:8000/about     -> ALSO index.html (SPA client-side routing fallback)
       http://127.0.0.1:8000/assets/app.js
       http://127.0.0.1:8000/api/hello -> the API, matched BEFORE the frontend
       http://127.0.0.1:8000/admin/    -> a second frontend mounted through a router

Why app.frontend() instead of StaticFiles(html=True)?
    - API routes are matched FIRST, the frontend is a low-priority catch-all.
    - Unknown paths fall back to index.html (or 404.html) so client-side routers work.
      The index.html fallback only applies to BROWSER NAVIGATIONS, i.e. requests whose
      `Accept` header includes text/html. `curl /about` (Accept: */*) still gets a JSON 404,
      so a JS `fetch()` to a typo'd API URL doesn't silently receive HTML.
      Test it:  curl -H "Accept: text/html" http://127.0.0.1:8000/about
    - `check_dir="auto"`: in `fastapi dev` a missing directory only warns
      (handy before you've run `npm run build`); in prod it errors at startup.

Typical workflow:  cd frontend && npm run build  ->  ../dist  ->  app.frontend("/", directory="dist")
"""

from fastapi import APIRouter, FastAPI

app = FastAPI()


# 1) API routes first (order doesn't actually matter, frontend is always lowest priority,
#    but keeping the API on a /api prefix avoids any confusion with frontend paths).
@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI"}


# 2) Serve the built frontend at "/".
#    fallback="auto": serve index.html for unknown paths if it exists, else 404.html.
app.frontend("/", directory="23_frontend_dist")


# 3) A second frontend under a router prefix (e.g. an admin panel built separately).
#    The router prefix is applied normally when included.
admin_router = APIRouter(prefix="/admin")
admin_router.frontend("/", directory="23_frontend_dist")  # reuse the same build for the demo
app.include_router(admin_router)
