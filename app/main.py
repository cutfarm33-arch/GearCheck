from __future__ import annotations

from fastapi import FastAPI

from .database import init_db
from .routers import items, jobs, transactions, users

init_db()

app = FastAPI(title="GearCheck", version="0.1.0")

app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(items.router)
app.include_router(transactions.router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
