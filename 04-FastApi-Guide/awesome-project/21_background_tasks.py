"""
21 - Background Tasks: do work AFTER the response is sent (emails, logs, webhooks).

Run:   fastapi dev 21_background_tasks.py

Declare a parameter `background_tasks: BackgroundTasks` and call
`.add_task(func, *args, **kwargs)`. The client gets the response immediately;
the task runs afterwards in the same process.

    - Sync task function  -> runs in a threadpool
    - Async task function -> awaited on the event loop
    - Works inside dependencies too (tasks are collected and all run after the response)

Use this for SMALL work. For heavy/long jobs (minutes, retries, many workers)
use a real queue: Celery, arq, RQ, Dramatiq, etc.

Try:
    POST /send-notification/allen@example.com?q=hello   -> instant 200; watch console + ./log.txt
    GET  /report                                        -> returns at once, "report" done later
"""

import time
from typing import Annotated

import anyio
from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()


# ---------------------------------------------------------------------------
# 1) A blocking task function (sync). Note: no `await` inside.
# ---------------------------------------------------------------------------
def write_notification(email: str, message: str = ""):
    time.sleep(2)  # simulate a slow email provider
    with open("log.txt", mode="a") as f:
        f.write(f"notification for {email}: {message}\n")
    print(f"[bg] sent notification to {email}")


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}  # returned right away


# ---------------------------------------------------------------------------
# 2) Background task added from a DEPENDENCY. FastAPI merges all tasks and
#    runs them in order after the response.
# ---------------------------------------------------------------------------
def write_log(message: str):
    with open("log.txt", mode="a") as f:
        f.write(message)


def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        background_tasks.add_task(write_log, f"found query: {q}\n")
    return q


@app.post("/send-notification-with-log/{email}")
async def send_notification_with_log(
    email: str,
    background_tasks: BackgroundTasks,
    q: Annotated[str | None, Depends(get_query)],
):
    background_tasks.add_task(write_log, f"message to {email}\n")
    return {"message": "Message sent", "q": q}


# ---------------------------------------------------------------------------
# 3) Async task function.
# ---------------------------------------------------------------------------
async def build_report(report_id: int):
    await anyio.sleep(3)
    print(f"[bg] report {report_id} ready")


@app.get("/report", status_code=202)  # 202 Accepted = "we took the job"
async def request_report(background_tasks: BackgroundTasks):
    background_tasks.add_task(build_report, 42)
    return {"status": "accepted", "report_id": 42}
