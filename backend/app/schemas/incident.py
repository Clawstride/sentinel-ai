"""
Pydantic schemas for the Incident Management module.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_INCIDENT_STATUS = "Open"


class IncidentStatus(str, Enum):
    """The only statuses an analyst may set an incident to."""

    OPEN = "Open"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"


class IncidentRead(BaseModel):
    """Represents an Incident as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: str
    title: str
    incident_type: str
    severity: str
    risk_score: int
    status: str
    username: str
    source_ip: str | None
    window_start: datetime | None
    window_end: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class IncidentGenerateResponse(BaseModel):
    """Response returned after running incident generation from detections."""

    message: str = Field(..., examples=["Incident generation completed"])
    incidents_created: int = Field(..., examples=[2])


class IncidentStatusUpdate(BaseModel):
    """Request body for PATCH /incidents/{incident_id}/status."""

    status: IncidentStatus


class IncidentNotesUpdate(BaseModel):
    """Request body for PATCH /incidents/{incident_id}/notes."""

    notes: str = Field(..., min_length=1, max_length=2000)
