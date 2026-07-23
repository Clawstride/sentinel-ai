"""
Service layer for the Dashboard Summary endpoint.

All counts come directly from the incidents table — nothing here is
static or fabricated. For this MVP's data volumes, fetching all
incidents once and aggregating in Python is simpler and just as
correct as several separate SQL COUNT/GROUP BY queries.
"""

from collections import Counter

from app.repositories.incident_repository import IncidentRepository
from app.schemas.dashboard import DashboardSummary


class DashboardService:
    """Builds real, database-derived incident metrics for a dashboard view."""

    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def get_summary(self) -> DashboardSummary:
        incidents = self.repository.get_all()

        status_counts = Counter(incident.status for incident in incidents)
        severity_counts = Counter(incident.severity for incident in incidents)
        type_counts = Counter(incident.incident_type for incident in incidents)

        return DashboardSummary(
            total_incidents=len(incidents),
            open_incidents=status_counts.get("Open", 0),
            investigating_incidents=status_counts.get("Investigating", 0),
            resolved_incidents=status_counts.get("Resolved", 0),
            false_positive_incidents=status_counts.get("False Positive", 0),
            high_incidents=severity_counts.get("High", 0),
            medium_incidents=severity_counts.get("Medium", 0),
            low_incidents=severity_counts.get("Low", 0),
            incidents_by_type=dict(type_counts),
        )
