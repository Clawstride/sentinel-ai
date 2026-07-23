"""
Pydantic schema for the Dashboard Summary endpoint.
"""

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    """Real, database-derived incident counts for a dashboard view."""

    total_incidents: int
    open_incidents: int
    investigating_incidents: int
    resolved_incidents: int
    false_positive_incidents: int

    # NOTE: the existing severity scheme (set when Incidents were first
    # introduced) is High / Medium / Low, not Critical/High/Medium/Low.
    # Kept as-is here rather than introducing a new tier, per the
    # instruction not to change existing working behavior unnecessarily.
    high_incidents: int
    medium_incidents: int
    low_incidents: int

    incidents_by_type: dict[str, int] = Field(
        default_factory=dict, description="Incident count grouped by incident_type"
    )
