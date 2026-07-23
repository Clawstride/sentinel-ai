"""
Service layer for the Investigation Workspace.

Orchestrates, for a single incident:
  1. Reconstruct its evidence timeline from LogEvent, using the
     incident's stored window_start/window_end.
  2. Generate deterministic indicators from that timeline + incident
     data (app/services/investigation/indicators.py — no AI).
  3. Look up the fixed recommended actions for its detection type
     (app/services/investigation/recommended_actions.py — no AI).
  4. Generate an analyst-friendly summary (AI if configured, otherwise
     a deterministic fallback — app/services/investigation/ai_summary.py).

Detection logic, risk scores, and severity are never touched here —
this service only reads what the Incident already has.
"""

import logging

from app.models.incident import Incident
from app.models.log_event import LogEvent
from app.repositories.incident_repository import IncidentRepository
from app.repositories.log_event_repository import LogEventRepository
from app.schemas.investigation import AISummary, InvestigationDetails, TimelineEntry
from app.services.investigation.ai_summary import generate_ai_summary
from app.services.investigation.indicators import build_indicators
from app.services.investigation.recommended_actions import get_recommended_actions

logger = logging.getLogger(__name__)


class InvestigationService:
    """Builds the full investigation view for one incident."""

    def __init__(self, incident_repository: IncidentRepository, log_event_repository: LogEventRepository):
        self.incident_repository = incident_repository
        self.log_event_repository = log_event_repository

    def get_investigation(self, incident_id: str) -> InvestigationDetails | None:
        """Returns the full investigation details for one incident, or None if not found."""
        incident = self.incident_repository.get_by_incident_id(incident_id)
        if incident is None:
            return None

        timeline_events = self._get_timeline(incident)
        indicators = build_indicators(incident, timeline_events)
        recommended_actions = get_recommended_actions(incident.incident_type)

        ai_context = self._build_ai_context(incident, indicators, timeline_events, recommended_actions)
        summary_text, generated_by = generate_ai_summary(ai_context)

        return InvestigationDetails(
            incident_id=incident.incident_id,
            title=incident.title,
            incident_type=incident.incident_type,
            severity=incident.severity,
            risk_score=incident.risk_score,
            status=incident.status,
            username=incident.username,
            indicators=indicators,
            timeline=[TimelineEntry.model_validate(event) for event in timeline_events],
            recommended_actions=recommended_actions,
            ai_summary=AISummary(summary=summary_text, generated_by=generated_by),
        )

    def _get_timeline(self, incident: Incident) -> list[LogEvent]:
        """
        Reconstructs the evidence timeline from the incident's stored
        window. Falls back to created_at if window_start/window_end are
        somehow missing (defensive only — every incident-creation path
        sets both).
        """
        start = incident.window_start or incident.created_at
        end = incident.window_end or incident.created_at
        return self.log_event_repository.get_events_for_username_in_window(incident.username, start, end)

    @staticmethod
    def _build_ai_context(
        incident: Incident,
        indicators: list[str],
        timeline_events: list[LogEvent],
        recommended_actions: list[str],
    ) -> dict:
        """
        Assembles exactly the structured, already-determined facts the AI
        summary is allowed to use — nothing more. See ai_summary.py for
        the grounding rules enforced in the prompt itself.
        """
        return {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type,
            "username": incident.username,
            "severity": incident.severity,
            "risk_score": incident.risk_score,
            "status": incident.status,
            "indicators": indicators,
            "timeline": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "ip_address": event.ip_address,
                    "country": event.country,
                    "device": event.device,
                    "login_status": event.login_status,
                }
                for event in timeline_events
            ],
            "recommended_actions": recommended_actions,
        }
