"""
Impossible Travel Detection service.

Rule:
  - Same username
  - Two successful authentication events
  - From different countries
  - Less than 2 hours apart

MVP notes:
  - Each successful login is compared to the immediately preceding
    successful login for that username (chronologically) — a
    "session-to-session" check, not every possible pair of logins.
    This matches the previous/current field naming in the response.
  - No geographic distance/velocity calculation — a country change
    within the time window is sufficient for this MVP, as specified.
  - Fixed risk score: 80 (High). A confirmed country change within 2
    hours is a strong signal of a compromised or shared credential.
"""

import logging
from collections import defaultdict
from datetime import timedelta

from app.repositories.log_event_repository import LogEventRepository
from app.schemas.detection import DetectionType, ImpossibleTravelDetection

logger = logging.getLogger(__name__)


class ImpossibleTravelDetectionService:
    """Detects impossible-travel login patterns from stored authentication logs."""

    RISK_SCORE = 80
    WINDOW = timedelta(hours=2)

    def __init__(self, repository: LogEventRepository):
        self.repository = repository

    def detect(self) -> list[ImpossibleTravelDetection]:
        """Runs impossible-travel detection across all stored successful logins."""
        events = self.repository.get_successful_login_events()

        events_by_user: dict[str, list] = defaultdict(list)
        for event in events:
            events_by_user[event.username].append(event)

        detections: list[ImpossibleTravelDetection] = []
        for username, user_events in events_by_user.items():
            user_events.sort(key=lambda e: e.timestamp)

            for previous_event, current_event in zip(user_events, user_events[1:]):
                time_gap = current_event.timestamp - previous_event.timestamp
                if previous_event.country != current_event.country and time_gap <= self.WINDOW:
                    detections.append(
                        ImpossibleTravelDetection(
                            detection_type=DetectionType.IMPOSSIBLE_TRAVEL,
                            username=username,
                            previous_country=previous_event.country,
                            current_country=current_event.country,
                            previous_timestamp=previous_event.timestamp,
                            current_timestamp=current_event.timestamp,
                            previous_ip_address=previous_event.ip_address,
                            current_ip_address=current_event.ip_address,
                            risk_score=self.RISK_SCORE,
                        )
                    )

        logger.info(f"Impossible travel detection run found {len(detections)} detection(s)")
        return detections
