"""
Pydantic schemas for the Detection feature.

`DetectionType` centralizes the set of detection rule names so future
detections (e.g. impossible travel, unusual device) reuse the same
enum instead of hardcoding strings across the codebase.

`BruteForceDetection` is the response shape for brute-force results.
It's deliberately generic enough (detection_type, risk_score) that
other detection rules can reuse the same base shape later, which
keeps this feature modular for when Incidents are built on top of it.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DetectionType(str, Enum):
    BRUTE_FORCE = "Brute Force"
    IMPOSSIBLE_TRAVEL = "Impossible Travel"
    NEW_DEVICE = "New Device Login"
    PRIVILEGED_LOGIN = "Suspicious Privileged Login"


class BruteForceDetection(BaseModel):
    """A single brute-force detection result for one username."""

    detection_type: DetectionType = Field(default=DetectionType.BRUTE_FORCE)
    username: str
    failed_attempts: int = Field(..., ge=1, description="Number of failed logins in the detected window")
    risk_score: int = Field(..., description="Fixed severity score assigned to this detection type")
    first_attempt_timestamp: datetime
    last_attempt_timestamp: datetime


class ImpossibleTravelDetection(BaseModel):
    """
    A single impossible-travel detection: the same username had two
    successful logins from different countries less than 2 hours apart.
    """

    detection_type: DetectionType = Field(default=DetectionType.IMPOSSIBLE_TRAVEL)
    username: str
    previous_country: str
    current_country: str
    previous_timestamp: datetime
    current_timestamp: datetime
    previous_ip_address: str
    current_ip_address: str
    risk_score: int = Field(..., description="Fixed severity score assigned to this detection type")


class NewDeviceDetection(BaseModel):
    """
    A single new-device detection: a successful login from a device
    never seen before for this username, plus at least one more
    suspicious signal (new IP or off-hours).
    """

    detection_type: DetectionType = Field(default=DetectionType.NEW_DEVICE)
    username: str
    device: str
    ip_address: str
    timestamp: datetime
    triggered_signals: list[str] = Field(
        ..., description="Which signals fired, e.g. ['new_device', 'new_ip']"
    )
    risk_score: int = Field(..., description="Fixed severity score assigned to this detection type")


class PrivilegedLoginDetection(BaseModel):
    """
    A single suspicious privileged-login detection: a privileged
    account logged in successfully with at least one suspicious signal
    (new IP, country change, or off-hours).
    """

    detection_type: DetectionType = Field(default=DetectionType.PRIVILEGED_LOGIN)
    username: str
    ip_address: str
    country: str
    timestamp: datetime
    triggered_signals: list[str] = Field(
        ..., description="Which signals fired, e.g. ['new_ip', 'country_change', 'off_hours']"
    )
    risk_score: int = Field(..., description="Fixed severity score assigned to this detection type")
