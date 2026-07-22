"""
Health check endpoint.

Used to verify that the API process is up and responding.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict:
    """Returns a simple status payload confirming the API is running."""
    logger.info("Health check requested")
    return {"status": "healthy"}
