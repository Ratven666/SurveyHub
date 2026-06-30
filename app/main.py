import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.db import base

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Возвращает полный traceback в теле ответа вместо глухого 500."""
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}
