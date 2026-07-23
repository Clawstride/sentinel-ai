"""
Pydantic schemas for the Investigation Workspace.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TimelineEntry(BaseModel):
    """One authentication event shown in an incident's evidence timeline."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    ip_address: str
    country: str
    device: str
    login_status: str


class SummarySource(str, Enum):
    """Where the analyst-facing summary text came from."""

    AI = "ai"
    FALLBACK = "fallback"


class AISummary(BaseModel):
    """The analyst-facing explanation of an incident."""

    summary: str
    generated_by: SummarySource = Field(
        ..., description="'ai' if an AI provider generated this, 'fallback' if it's the deterministic template."
    )


class InvestigationDetails(BaseModel):
    """Full response for GET /incidents/{incident_id}/investigation."""

    incident_id: str
    title: str
    incident_type: str
    severity: str
    risk_score: int
    status: str
    username: str

    indicators: list[str] = Field(..., description="Deterministic reasons the rule engine flagged this incident")
    timeline: list[TimelineEntry] = Field(..., description="Authentication events backing this incident")
    recommended_actions: list[str] = Field(..., description="Deterministic next steps for the analyst")
    ai_summary: AISummary
