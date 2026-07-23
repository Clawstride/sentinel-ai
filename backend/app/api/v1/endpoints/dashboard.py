"""
Dashboard endpoints.

GET /dashboard/summary returns real, database-derived incident counts
for a future frontend dashboard. This endpoint only handles HTTP
concerns — the aggregation logic lives in DashboardService.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """Wires the repository into the dashboard service (manual DI, matching the rest of the app)."""
    repository = IncidentRepository(db)
    return DashboardService(repository)


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get database-derived incident summary metrics",
)
def get_dashboard_summary(service: DashboardService = Depends(get_dashboard_service)) -> DashboardSummary:
    """Returns real-time incident counts by status, severity, and type."""
    return service.get_summary()
