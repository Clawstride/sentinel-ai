"""
Incident Management endpoints.

- POST /incidents/generate  — runs every implemented detection rule
  (Brute Force, Impossible Travel, New Device, Suspicious Privileged
  Login) and creates Incident records from the results.
- GET  /incidents           — lists all incidents, newest first.
- GET  /incidents/{incident_id} — fetches a single incident.

These endpoints only handle HTTP concerns (DB session, dependency
wiring, 404 translation) — all business logic lives in IncidentService.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.incident_repository import IncidentRepository
from app.repositories.log_event_repository import LogEventRepository
from app.schemas.incident import IncidentGenerateResponse, IncidentRead
from app.services.detection.brute_force_detection_service import BruteForceDetectionService
from app.services.detection.impossible_travel_detection_service import ImpossibleTravelDetectionService
from app.services.detection.new_device_detection_service import NewDeviceDetectionService
from app.services.detection.privileged_login_detection_service import PrivilegedLoginDetectionService
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    """Wires repositories and all 4 detection services into IncidentService."""
    incident_repository = IncidentRepository(db)
    log_event_repository = LogEventRepository(db)

    return IncidentService(
        repository=incident_repository,
        brute_force_service=BruteForceDetectionService(log_event_repository),
        impossible_travel_service=ImpossibleTravelDetectionService(log_event_repository),
        new_device_service=NewDeviceDetectionService(log_event_repository),
        privileged_login_service=PrivilegedLoginDetectionService(log_event_repository),
        db=db,
    )


@router.post(
    "/generate",
    response_model=IncidentGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate incidents from all detection rules",
)
def generate_incidents(
    service: IncidentService = Depends(get_incident_service),
) -> IncidentGenerateResponse:
    """
    Runs Brute Force, Impossible Travel, New Device, and Suspicious
    Privileged Login detection, and creates one Incident per detection
    that doesn't already have one.
    """
    incidents_created = service.generate_incidents()
    return IncidentGenerateResponse(
        message="Incident generation completed",
        incidents_created=incidents_created,
    )


@router.get(
    "",
    response_model=list[IncidentRead],
    summary="List all incidents (newest first)",
)
def list_incidents(service: IncidentService = Depends(get_incident_service)) -> list[IncidentRead]:
    """Returns every incident, ordered by creation time descending."""
    return service.list_incidents()


@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Get a single incident by incident_id",
)
def get_incident(incident_id: str, service: IncidentService = Depends(get_incident_service)) -> IncidentRead:
    """Returns one incident by its human-friendly ID, e.g. 'INC-000001'."""
    incident = service.get_incident(incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return incident
