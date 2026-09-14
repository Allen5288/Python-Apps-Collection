"""
09 - File uploads: `File()` (bytes) vs `UploadFile`, multiple files, files + form.

Run:   fastapi dev 09_files.py

`bytes` + File()  -> whole file read into memory. Fine for small files.
`UploadFile`      -> spooled to disk after a size threshold, async API,
                     you get filename / content_type / .read() / .seek(). Prefer this.

Try (use /docs, it renders a file picker), or curl:
    curl -F "file=@README.md" http://127.0.0.1:8000/files/
    curl -F "file=@README.md" http://127.0.0.1:8000/uploadfile/
    curl -F "files=@a.txt" -F "files=@b.txt" http://127.0.0.1:8000/uploadfiles/
    curl -F "file=@a.txt" -F "token=abc" http://127.0.0.1:8000/files-and-form/
    open http://127.0.0.1:8000/          -> tiny HTML upload form
"""

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) Small file as raw bytes.
# ---------------------------------------------------------------------------
@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


# ---------------------------------------------------------------------------
# 2) UploadFile: no need for File() unless you add metadata.
# ---------------------------------------------------------------------------
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()  # async read; or `file.file` for the sync file-like object
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "first_bytes": contents[:20].decode(errors="replace"),
    }


# ---------------------------------------------------------------------------
# 3) Optional file: `UploadFile | None = None`.
#    Add File(description=...) for docs metadata.
# ---------------------------------------------------------------------------
@app.post("/uploadfile/optional")
async def create_upload_file_optional(
    file: Annotated[UploadFile | None, File(description="Optional file to upload")] = None,
):
    if not file:
        return {"message": "No upload file sent"}
    return {"filename": file.filename}


# ---------------------------------------------------------------------------
# 4) Multiple files: list[UploadFile]. Same form field name repeated.
# ---------------------------------------------------------------------------
@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [f.filename for f in files]}


# ---------------------------------------------------------------------------
# 5) Files + form fields together (both are multipart/form-data, so OK).
#    You CANNOT add a JSON body param here.
# ---------------------------------------------------------------------------
@app.post("/files-and-form/")
async def create_file_and_form(
    file: UploadFile,
    token: Annotated[str, Form()],
    note: Annotated[str | None, Form()] = None,
):
    return {"filename": file.filename, "token": token, "note": note}


# ---------------------------------------------------------------------------
# 6) Save an upload to disk in chunks (don't load big files fully into memory).
# ---------------------------------------------------------------------------
from pathlib import Path  # noqa: E402

UPLOAD_DIR = Path(".uploads")


@app.post("/uploadfile/save")
async def save_upload_file(file: UploadFile):
    UPLOAD_DIR.mkdir(exist_ok=True)
    dest = UPLOAD_DIR / (file.filename or "unnamed")
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1 MiB at a time
            out.write(chunk)
            size += len(chunk)
    return {"saved_to": str(dest), "size": size}


# ---------------------------------------------------------------------------
# 7) A minimal HTML page so you can test from the browser.
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def main():
    return """
<body>
<h3>bytes</h3>
<form action="/files/" enctype="multipart/form-data" method="post">
  <input name="file" type="file"><input type="submit">
</form>
<h3>multiple UploadFile</h3>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
  <input name="files" type="file" multiple><input type="submit">
</form>
</body>
"""
