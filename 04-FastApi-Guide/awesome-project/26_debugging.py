"""
26 - Debugging: run uvicorn from Python so your IDE debugger (VS Code / PyCharm)
     can attach, hit breakpoints, and inspect variables.

Ways to run:
    1) fastapi dev 26_debugging.py            normal dev server (auto-reload)
    2) uv run python 26_debugging.py          runs the `if __name__ == "__main__"` block
    3) In VS Code: open this file, press F5 with the launch config below,
       set a breakpoint inside `root()` and open http://127.0.0.1:8000/

VS Code  .vscode/launch.json:
    {
      "version": "0.2.0",
      "configurations": [
        {
          "name": "FastAPI: current file",
          "type": "debugpy",
          "request": "launch",
          "program": "${file}",
          "console": "integratedTerminal",
          "justMyCode": true
        },
        {
          "name": "FastAPI: uvicorn module",
          "type": "debugpy",
          "request": "launch",
          "module": "uvicorn",
          "args": ["26_debugging:app", "--reload", "--port", "8000"],
          "jinja": true
        }
      ]
    }

PyCharm: Run > Edit Configurations > + Python > Script path = this file. Then Debug.

Why `__name__ == "__main__"`?
    - `python 26_debugging.py`   -> __name__ == "__main__" -> uvicorn.run() executes.
    - `fastapi dev 26_debugging.py` / `import 26_debugging` -> __name__ == "26_debugging"
      -> the block is skipped, so the app can be imported without starting a server.

Gotcha: `reload=True` with uvicorn.run() requires passing the app as an IMPORT
STRING ("26_debugging:app"), not the object, because the reloader spawns a new
process that has to import it. Debuggers generally work better with reload=False.
"""

import logging

import uvicorn
from fastapi import FastAPI

# Standard logging goes to the uvicorn console. Use it instead of print() in real apps.
logger = logging.getLogger("uvicorn.error")  # reuse uvicorn's configured logger

app = FastAPI()


@app.get("/")
async def root():
    a = "hello"
    b = "world"
    logger.info("root called, a=%s b=%s", a, b)
    # Set a BREAKPOINT on the next line in your IDE, or uncomment:
    # breakpoint()   # drops into pdb in the terminal (only without --reload)
    return {"message": f"{a} {b}"}


@app.get("/divide")
async def divide(x: int, y: int):
    # /divide?x=1&y=0 -> ZeroDivisionError -> 500 and a full traceback in the console.
    # With the debugger attached and "raised exceptions" enabled, it pauses right here.
    return {"result": x / y}


if __name__ == "__main__":
    # Options mirror the CLI flags: uvicorn 26_debugging:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        app,  # pass the object -> debugger sees this process; no reload
        host="127.0.0.1",
        port=8000,
        log_level="debug",  # "critical" | "error" | "warning" | "info" | "debug" | "trace"
        # reload=True,      # would need "26_debugging:app" as the first argument instead of `app`
    )
