"""
FastAPI application entrypoint.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.utils.exceptions import InvalidCSVError, InvalidFileTypeError, MissingColumnsError

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Security Investigation Assistant — backend API.",
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    # Local Vite dev servers only. This is the minimum change needed to let
    # the SentinelAI frontend (localhost:5173) call this API during
    # development; it does not affect any other backend behavior.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(InvalidFileTypeError)
async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(InvalidCSVError)
async def invalid_csv_handler(request: Request, exc: InvalidCSVError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(MissingColumnsError)
async def missing_columns_handler(request: Request, exc: MissingColumnsError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": {"message": "Missing required columns", "missing_columns": exc.missing_columns}},
    )


@app.on_event("startup")
def on_startup() -> None:
    logger.info(f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode")


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info(f"Shutting down {settings.APP_NAME}")
