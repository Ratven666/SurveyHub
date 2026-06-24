from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

from app.db import base

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
