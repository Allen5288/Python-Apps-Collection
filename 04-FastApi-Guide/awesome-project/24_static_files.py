"""
24 - Static Files with `StaticFiles` (CSS, images, downloads, plain files).

Run:   fastapi dev 24_static_files.py
Open:  http://127.0.0.1:8000/static/style.css
       http://127.0.0.1:8000/static/hello.txt
       http://127.0.0.1:8000/                -> HTML page that links the CSS
       http://127.0.0.1:8000/download        -> FileResponse with a download filename

`app.mount(path, StaticFiles(directory=...), name=...)`
    - "mount" = a whole independent sub-application at that path prefix.
      Everything under /static/* is handled by StaticFiles, not by your routes.
    - `name` is used by `request.url_for("static", path="style.css")` to build URLs.
    - Static mounts do NOT appear in /docs (not part of OpenAPI).

Static files vs frontend():  use StaticFiles for plain asset folders; use
app.frontend() (23_frontend.py) for SPA builds that need an index.html fallback.
"""

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount: /static/<anything> -> ./24_static/static/<anything>
app.mount("/static", StaticFiles(directory="24_static/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Build the URL from the mount name instead of hard-coding "/static/style.css".
    # `request.url_for("static", path=...)` is the usual one-liner and works when this
    # app runs standalone. When the app is itself MOUNTED inside another app (main.py hub),
    # url_for resolves names against the OUTER router and fails. So: ask THIS app's router
    # for the path, and prepend `root_path` (the mount prefix, "" when standalone).
    prefix = request.scope.get("root_path", "")
    css_url = prefix + request.app.url_path_for("static", path="style.css")
    return f"""
<!doctype html>
<html>
<head><link rel="stylesheet" href="{css_url}"></head>
<body>
  <h1>Static files demo</h1>
  <p>This page is styled by <a href="{css_url}">{css_url}</a></p>
  <p><a href="{prefix}/static/hello.txt">hello.txt</a> | <a href="{prefix}/download">download hello.txt</a></p>
</body>
</html>
"""


# Serve ONE file from a route (e.g. generated report), with Content-Disposition
# so the browser downloads it under the given name.
@app.get("/download")
async def download():
    return FileResponse(
        "24_static/static/hello.txt",
        media_type="text/plain",
        filename="greeting.txt",  # -> Content-Disposition: attachment; filename="greeting.txt"
    )
