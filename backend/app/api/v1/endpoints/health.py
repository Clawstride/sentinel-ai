"""
Health check endpoint.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict:
    logger.info("Health check requested")
    return {"status": "healthy"}
