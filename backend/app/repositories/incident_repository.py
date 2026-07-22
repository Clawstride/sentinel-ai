"""
Repository layer for Incident.

Handles only database access for the Incident model. Duplicate
detection, severity mapping, and pulling data from detections all
live in the service layer (app/services/incident_service.py).
"""

import logging

from sqlalchemy.orm import Session

from app.models.incident import Incident

logger = logging.getLogger(__name__)


class IncidentRepository:
    """Handles all direct database operations for Incident rows."""

    def __init__(self, db: Session):
        self.db = db

    def exists(self, username: str, incident_type: str, title: str) -> bool:
        """
        Checks whether an incident already exists for this exact
        username + incident_type + title combination.

        `title` is built by the service layer to include the detected
        time window, so this check effectively prevents creating a
        duplicate incident for the same detected burst while still
        allowing separate bursts for the same user to become separate
        incidents.
        """
        return (
            self.db.query(Incident)
            .filter(
                Incident.username == username,
                Incident.incident_type == incident_type,
                Incident.title == title,
            )
            .first()
            is not None
        )

    def create(self, incident: Incident) -> Incident:
        """
        Persists a new incident and assigns its human-friendly
        `incident_id` (e.g. "INC-000001") from the generated primary key.
        """
        self.db.add(incident)
        self.db.flush()  # assigns incident.id without committing yet

        incident.incident_id = f"INC-{incident.id:06d}"

        self.db.commit()
        self.db.refresh(incident)

        logger.info(f"Created incident {incident.incident_id} for username={incident.username!r}")
        return incident

    def get_all(self) -> list[Incident]:
        """Returns all incidents, newest first."""
        return self.db.query(Incident).order_by(Incident.created_at.desc()).all()

    def get_by_incident_id(self, incident_id: str) -> Incident | None:
        """Returns a single incident by its human-friendly incident_id, or None."""
        return self.db.query(Incident).filter(Incident.incident_id == incident_id).first()
