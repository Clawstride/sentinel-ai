"""
Incident Management endpoints.

- POST  /incidents/generate  — runs every implemented detection rule
  (Brute Force, Impossible Travel, New Device, Suspicious Privileged
  Login) and creates Incident records from the results.
- GET   /incidents           — lists all incidents, newest first.
- GET   /incidents/{incident_id} — fetches a single incident.
- GET   /incidents/{incident_id}/investigation — evidence, indicators,
  recommended actions, and an AI-assisted (or fallback) summary.
- PATCH /incidents/{incident_id}/status — updates status.
- PATCH /incidents/{incident_id}/notes — updates analyst notes.

These endpoints only handle HTTP concerns (DB session, dependency
wiring, 404 translation) — all business logic lives in IncidentService
and InvestigationService.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.incident_repository import IncidentRepository
from app.repositories.log_event_repository import LogEventRepository
from app.schemas.incident import (
    IncidentGenerateResponse,
    IncidentNotesUpdate,
    IncidentRead,
    IncidentStatusUpdate,
)
from app.schemas.investigation import InvestigationDetails
from app.services.detection.brute_force_detection_service import BruteForceDetectionService
from app.services.detection.impossible_travel_detection_service import ImpossibleTravelDetectionService
from app.services.detection.new_device_detection_service import NewDeviceDetectionService
from app.services.detection.privileged_login_detection_service import PrivilegedLoginDetectionService
from app.services.incident_service import IncidentService
from app.services.investigation_service import InvestigationService

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


def get_investigation_service(db: Session = Depends(get_db)) -> InvestigationService:
    """Wires repositories into InvestigationService."""
    incident_repository = IncidentRepository(db)
    log_event_repository = LogEventRepository(db)
    return InvestigationService(incident_repository, log_event_repository)


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


@router.get(
    "/{incident_id}/investigation",
    response_model=InvestigationDetails,
    summary="Get full investigation details for one incident",
)
def get_incident_investigation(
    incident_id: str,
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationDetails:
    """
    Returns everything an analyst needs to understand an incident:
    deterministic indicators (why it was flagged), the evidence
    timeline (the actual LogEvent rows behind it), fixed recommended
    next steps, and an analyst-friendly summary (AI-generated if
    configured, otherwise a deterministic fallback — this endpoint
    always returns a usable summary either way).
    """
    investigation = service.get_investigation(incident_id)
    if investigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return investigation


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentRead,
    summary="Update an incident's status",
)
def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentRead:
    """Sets status to one of: Open, Investigating, Resolved, False Positive."""
    incident = service.update_status(incident_id, payload.status.value)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return incident


@router.patch(
    "/{incident_id}/notes",
    response_model=IncidentRead,
    summary="Update an incident's analyst notes",
)
def update_incident_notes(
    incident_id: str,
    payload: IncidentNotesUpdate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentRead:
    """Sets (replaces) the free-text analyst notes on an incident."""
    incident = service.update_notes(incident_id, payload.notes)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return incident
