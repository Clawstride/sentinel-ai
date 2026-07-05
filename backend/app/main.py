"""
FastAPI application entrypoint.

Responsible for:
  - Creating the FastAPI app instance.
  - Configuring logging on startup.
  - Registering API routers.

Run locally with:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Security Investigation Assistant — backend API.",
    version="0.1.0",
    debug=settings.DEBUG,
)

# /health is mounted at the root (not under /api/v1) since it's an
# infrastructure/monitoring endpoint (used by load balancers, Docker
# healthchecks, uptime monitors), not a versioned business API.
app.include_router(health_router)

# All future business-logic endpoints will be versioned under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    logger.info(f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode")


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info(f"Shutting down {settings.APP_NAME}")
