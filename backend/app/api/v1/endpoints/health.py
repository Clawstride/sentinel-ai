"""
Health check endpoint.

Used to verify that the API process is up and responding. Later this
can be extended to check DB connectivity, but for this MVP foundation
it simply confirms the service is alive.
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
