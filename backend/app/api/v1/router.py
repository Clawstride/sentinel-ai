"""
Aggregates all v1 endpoint routers into a single router.

As new endpoint modules are added under app/api/v1/endpoints/, include
their routers here. This keeps app/main.py clean and free of growing
import lists.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import detections, incidents, logs

api_router = APIRouter()

api_router.include_router(logs.router)
api_router.include_router(detections.router)
api_router.include_router(incidents.router)
