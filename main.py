"""
Application entry point.

Creates the FastAPI app, includes the /ask route, and keeps the
original health check endpoint from Phase 0.
"""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"status": "ok"}