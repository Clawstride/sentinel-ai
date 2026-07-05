"""
Aggregates all v1 endpoint routers into a single router.

As new endpoint modules are added under app/api/v1/endpoints/, include
their routers here. This keeps app/main.py clean and free of growing
import lists.
"""

from fastapi import APIRouter

api_router = APIRouter()

# Future versioned endpoint routers get included here, e.g.:
# from app.api.v1.endpoints import cases
# api_router.include_router(cases.router)
