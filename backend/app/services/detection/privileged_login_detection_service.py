"""
Suspicious Privileged Login Detection service.

Rule:
  - is_privileged = true
  AND at least one of:
    - a new IP address for that username
    - a country change for that username
    - an off-hours authentication time

MVP notes:
  - "New IP" / "country change" are judged against the username's full
    successful-login history (privileged or not), scanned in
    chronological order — the baseline reflects everywhere the user
    has legitimately logged in before, not just their other privileged
    events.
  - A user's very first-ever successful login is never flagged for new
    IP/country (no baseline yet); off-hours can still fire on it.
  - Fixed MVP risk score: 90 (highest of the four rules). Privileged
    accounts are the highest-value target in the system, so any of
    these three signals on a privileged account is treated as high
    severity by design.
"""

import logging
from collections import defaultdict

from app.repositories.log_event_repository import LogEventRepository
from app.schemas.detection import DetectionType, PrivilegedLoginDetection
from app.services.detection.common import is_off_hours

logger = logging.getLogger(__name__)


class PrivilegedLoginDetectionService:
    """Detects suspicious privileged-account logins from stored authentication logs."""

    RISK_SCORE = 90

    def __init__(self, repository: LogEventRepository):
        self.repository = repository

    def detect(self) -> list[PrivilegedLoginDetection]:
        """Runs suspicious-privileged-login detection across all stored successful logins."""
        events = self.repository.get_successful_login_events()

        events_by_user: dict[str, list] = defaultdict(list)
        for event in events:
            events_by_user[event.username].append(event)

        detections: list[PrivilegedLoginDetection] = []
        for username, user_events in events_by_user.items():
            user_events.sort(key=lambda e: e.timestamp)

            seen_ips: set[str] = set()
            seen_countries: set[str] = set()

            for event in user_events:
                is_new_ip = bool(seen_ips) and event.ip_address not in seen_ips
                is_country_change = bool(seen_countries) and event.country not in seen_countries
                off_hours = is_off_hours(event.timestamp)

                if event.is_privileged and (is_new_ip or is_country_change or off_hours):
                    triggered_signals = []
                    if is_new_ip:
                        triggered_signals.append("new_ip")
                    if is_country_change:
                        triggered_signals.append("country_change")
                    if off_hours:
                        triggered_signals.append("off_hours")

                    detections.append(
                        PrivilegedLoginDetection(
                            detection_type=DetectionType.PRIVILEGED_LOGIN,
                            username=username,
                            ip_address=event.ip_address,
                            country=event.country,
                            timestamp=event.timestamp,
                            triggered_signals=triggered_signals,
                            risk_score=self.RISK_SCORE,
                        )
                    )

                seen_ips.add(event.ip_address)
                seen_countries.add(event.country)

        logger.info(f"Privileged login detection run found {len(detections)} detection(s)")
        return detections
