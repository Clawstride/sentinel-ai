"""
Pydantic schemas for the Incident Management module.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_INCIDENT_STATUS = "Open"


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
    created_at: datetime
    updated_at: datetime


class IncidentGenerateResponse(BaseModel):
    """Response returned after running incident generation from detections."""

    message: str = Field(..., examples=["Incident generation completed"])
    incidents_created: int = Field(..., examples=[2])
