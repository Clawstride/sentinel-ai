"""
Service layer for the Incident Management module.

Turns detection results into persisted Incident records. This service
calls each detection service's existing `detect()` method exactly as
it already works — no detection service is modified — and treats each
one purely as a data source. Adding a future 5th detection rule means
adding one constructor argument and one `_process_*` method here; nothing
about the existing rules changes.
"""

import logging

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.log_event import LogEvent
from app.repositories.incident_repository import IncidentRepository
from app.schemas.detection import (
    BruteForceDetection,
    ImpossibleTravelDetection,
    NewDeviceDetection,
    PrivilegedLoginDetection,
)
from app.services.detection.brute_force_detection_service import BruteForceDetectionService
from app.services.detection.impossible_travel_detection_service import ImpossibleTravelDetectionService
from app.services.detection.new_device_detection_service import NewDeviceDetectionService
from app.services.detection.privileged_login_detection_service import PrivilegedLoginDetectionService

logger = logging.getLogger(__name__)


class IncidentService:
    """Coordinates turning detection results (from all detection rules) into Incident records."""

    def __init__(
        self,
        repository: IncidentRepository,
        brute_force_service: BruteForceDetectionService,
        impossible_travel_service: ImpossibleTravelDetectionService,
        new_device_service: NewDeviceDetectionService,
        privileged_login_service: PrivilegedLoginDetectionService,
        db: Session,
    ):
        self.repository = repository
        self.brute_force_service = brute_force_service
        self.impossible_travel_service = impossible_travel_service
        self.new_device_service = new_device_service
        self.privileged_login_service = privileged_login_service
        # A read-only lookup against LogEvent (to find the source IP for a
        # brute-force detection, which has no IP of its own) is done
        # directly here rather than via LogEventRepository, so that
        # repository -- part of the already-complete upload feature --
        # stays untouched.
        self.db = db

    def generate_incidents(self) -> int:
        """
        Runs every implemented detection rule and creates an Incident for
        every detection that doesn't already have one. Returns the total
        number of incidents created across all rules.
        """
        created_count = 0
        created_count += self._process_bruteforce_detections()
        created_count += self._process_impossible_travel_detections()
        created_count += self._process_new_device_detections()
        created_count += self._process_privileged_login_detections()

        logger.info(f"Incident generation created {created_count} new incident(s) in total")
        return created_count

    def list_incidents(self) -> list[Incident]:
        """Returns all incidents, newest first."""
        return self.repository.get_all()

    def get_incident(self, incident_id: str) -> Incident | None:
        """Returns a single incident by its incident_id, or None if not found."""
        return self.repository.get_by_incident_id(incident_id)

    # ------------------------------------------------------------------
    # Per-rule processing
    #
    # Each method runs one detection rule and creates incidents for its
    # results. Kept separate (rather than one generic loop) because each
    # detection schema has different fields to build a title/source_ip
    # from.
    # ------------------------------------------------------------------

    def _process_bruteforce_detections(self) -> int:
        created = 0
        for detection in self.brute_force_service.detect():
            title = self._build_bruteforce_title(detection)
            source_ip = self._lookup_bruteforce_source_ip(detection)
            if self._create_incident_if_new(detection.username, detection.detection_type.value, title, detection.risk_score, source_ip):
                created += 1
        return created

    def _process_impossible_travel_detections(self) -> int:
        created = 0
        for detection in self.impossible_travel_service.detect():
            title = self._build_impossible_travel_title(detection)
            if self._create_incident_if_new(detection.username, detection.detection_type.value, title, detection.risk_score, detection.current_ip_address):
                created += 1
        return created

    def _process_new_device_detections(self) -> int:
        created = 0
        for detection in self.new_device_service.detect():
            title = self._build_new_device_title(detection)
            if self._create_incident_if_new(detection.username, detection.detection_type.value, title, detection.risk_score, detection.ip_address):
                created += 1
        return created

    def _process_privileged_login_detections(self) -> int:
        created = 0
        for detection in self.privileged_login_service.detect():
            title = self._build_privileged_login_title(detection)
            if self._create_incident_if_new(detection.username, detection.detection_type.value, title, detection.risk_score, detection.ip_address):
                created += 1
        return created

    # ------------------------------------------------------------------
    # Shared incident creation + dedup
    # ------------------------------------------------------------------

    def _create_incident_if_new(
        self,
        username: str,
        incident_type: str,
        title: str,
        risk_score: int,
        source_ip: str | None,
    ) -> bool:
        """
        Creates an Incident for this detection unless one already exists
        for the same username + incident_type + title. Returns True if a
        new incident was created, False if it was a duplicate.
        """
        if self.repository.exists(username=username, incident_type=incident_type, title=title):
            logger.info(f"Incident already exists for {username!r} ({incident_type}), skipping")
            return False

        incident = Incident(
            incident_id="PENDING",  # overwritten with INC-000001 style ID on create()
            title=title,
            incident_type=incident_type,
            severity=self._map_severity(risk_score),
            risk_score=risk_score,
            status="Open",
            username=username,
            source_ip=source_ip,
        )
        self.repository.create(incident)
        return True

    # ------------------------------------------------------------------
    # Title builders (one per detection type -- each encodes enough of
    # the detection's identifying fields that re-running detection on
    # the same data never creates a duplicate incident, while genuinely
    # distinct events for the same user each get their own incident).
    # ------------------------------------------------------------------

    @staticmethod
    def _build_bruteforce_title(detection: BruteForceDetection) -> str:
        return (
            f"Brute Force Login Attempts Detected for '{detection.username}' "
            f"({detection.first_attempt_timestamp.isoformat()} to "
            f"{detection.last_attempt_timestamp.isoformat()})"
        )

    @staticmethod
    def _build_impossible_travel_title(detection: ImpossibleTravelDetection) -> str:
        return (
            f"Impossible Travel Detected for '{detection.username}' "
            f"({detection.previous_country} -> {detection.current_country}, "
            f"{detection.previous_timestamp.isoformat()} to {detection.current_timestamp.isoformat()})"
        )

    @staticmethod
    def _build_new_device_title(detection: NewDeviceDetection) -> str:
        return (
            f"New Device Login Detected for '{detection.username}' "
            f"(device='{detection.device}', at {detection.timestamp.isoformat()})"
        )

    @staticmethod
    def _build_privileged_login_title(detection: PrivilegedLoginDetection) -> str:
        return (
            f"Suspicious Privileged Login Detected for '{detection.username}' "
            f"(ip='{detection.ip_address}', country='{detection.country}', "
            f"at {detection.timestamp.isoformat()})"
        )

    @staticmethod
    def _map_severity(risk_score: int) -> str:
        """Maps a numeric risk score to a severity label."""
        if risk_score >= 70:
            return "High"
        if risk_score >= 40:
            return "Medium"
        return "Low"

    def _lookup_bruteforce_source_ip(self, detection: BruteForceDetection) -> str | None:
        """
        Finds the source IP of the earliest failed login within the
        detected brute-force window. Only brute force needs this lookup;
        the other three detection schemas already carry an IP field
        directly from the log event that triggered them.
        """
        event = (
            self.db.query(LogEvent)
            .filter(
                LogEvent.username == detection.username,
                LogEvent.timestamp >= detection.first_attempt_timestamp,
                LogEvent.timestamp <= detection.last_attempt_timestamp,
            )
            .order_by(LogEvent.timestamp.asc())
            .first()
        )
        return event.ip_address if event else None
