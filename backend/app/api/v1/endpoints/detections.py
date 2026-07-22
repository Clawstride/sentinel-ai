"""
Detection endpoints.

GET /detections/bruteforce, /impossible-travel, /new-device, and
/privileged each run one detection rule over stored authentication
logs and return the results. These endpoints only handle HTTP concerns
(DB session, dependency wiring) — the detection logic itself lives in
the service layer, one file per rule under app/services/detection/.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.log_event_repository import LogEventRepository
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

router = APIRouter(prefix="/detections", tags=["Detections"])


def get_bruteforce_detection_service(db: Session = Depends(get_db)) -> BruteForceDetectionService:
    """Wires the repository into the detection service (manual DI, matching the rest of the app)."""
    repository = LogEventRepository(db)
    return BruteForceDetectionService(repository)


@router.get(
    "/bruteforce",
    response_model=list[BruteForceDetection],
    summary="Detect brute-force login attempts",
)
def get_bruteforce_detections(
    service: BruteForceDetectionService = Depends(get_bruteforce_detection_service),
) -> list[BruteForceDetection]:
    """
    Scans stored authentication logs for brute-force patterns: 5 or
    more failed login attempts by the same username within a rolling
    10-minute window. Returns one result per detected burst.
    """
    return service.detect()


def get_impossible_travel_detection_service(
    db: Session = Depends(get_db),
) -> ImpossibleTravelDetectionService:
    """Wires the repository into the detection service (manual DI, matching the rest of the app)."""
    repository = LogEventRepository(db)
    return ImpossibleTravelDetectionService(repository)


@router.get(
    "/impossible-travel",
    response_model=list[ImpossibleTravelDetection],
    summary="Detect impossible-travel logins",
)
def get_impossible_travel_detections(
    service: ImpossibleTravelDetectionService = Depends(get_impossible_travel_detection_service),
) -> list[ImpossibleTravelDetection]:
    """
    Scans stored successful logins for the same username authenticating
    from different countries less than 2 hours apart.
    """
    return service.detect()


def get_new_device_detection_service(db: Session = Depends(get_db)) -> NewDeviceDetectionService:
    """Wires the repository into the detection service (manual DI, matching the rest of the app)."""
    repository = LogEventRepository(db)
    return NewDeviceDetectionService(repository)


@router.get(
    "/new-device",
    response_model=list[NewDeviceDetection],
    summary="Detect new-device logins with an additional suspicious signal",
)
def get_new_device_detections(
    service: NewDeviceDetectionService = Depends(get_new_device_detection_service),
) -> list[NewDeviceDetection]:
    """
    Scans stored successful logins for a device never seen before for
    that username, combined with a new IP or an off-hours login time.
    """
    return service.detect()


def get_privileged_login_detection_service(
    db: Session = Depends(get_db),
) -> PrivilegedLoginDetectionService:
    """Wires the repository into the detection service (manual DI, matching the rest of the app)."""
    repository = LogEventRepository(db)
    return PrivilegedLoginDetectionService(repository)


@router.get(
    "/privileged",
    response_model=list[PrivilegedLoginDetection],
    summary="Detect suspicious privileged-account logins",
)
def get_privileged_login_detections(
    service: PrivilegedLoginDetectionService = Depends(get_privileged_login_detection_service),
) -> list[PrivilegedLoginDetection]:
    """
    Scans stored successful logins for privileged accounts (is_privileged
    = true) combined with a new IP, a country change, or an off-hours
    login time.
    """
    return service.detect()
