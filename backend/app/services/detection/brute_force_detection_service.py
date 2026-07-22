"""
Brute Force Detection service.

Detection rule:
  - Same username
  - 5 or more FAILED login attempts
  - Within a rolling 10-minute window

Implementation notes:
  - Failed-login events are read once from the repository (already
    sorted by username, then timestamp) and grouped in memory by
    username.
  - For each username, a two-pointer sliding window scans the sorted
    timestamps. Whenever the window reaches the failed-attempt
    threshold within the time limit, it is reported as one detection
    and the window resets from the event right after it — this keeps
    a continuous burst of failed logins from being reported as many
    overlapping detections for the same incident.

This service only reads log events and returns detection results; it
does not persist anything. Incident-creation logic will consume this
service's output later without needing to change it.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta

from app.repositories.log_event_repository import LogEventRepository
from app.schemas.detection import BruteForceDetection, DetectionType

logger = logging.getLogger(__name__)


class BruteForceDetectionService:
    """Detects brute-force login patterns from stored authentication logs."""

    FAILED_ATTEMPTS_THRESHOLD = 5
    WINDOW_MINUTES = 10
    RISK_SCORE = 70

    def __init__(self, repository: LogEventRepository):
        self.repository = repository

    def detect(self) -> list[BruteForceDetection]:
        """Runs brute-force detection across all stored log events."""
        failed_events = self.repository.get_failed_login_events()

        timestamps_by_user: dict[str, list[datetime]] = defaultdict(list)
        for event in failed_events:
            timestamps_by_user[event.username].append(event.timestamp)

        detections: list[BruteForceDetection] = []
        for username, timestamps in timestamps_by_user.items():
            # Repository already orders by username then timestamp, but
            # sorting again here keeps this method correct even if the
            # repository's ordering ever changes.
            timestamps.sort()
            for first_ts, last_ts, attempt_count in self._find_bursts(timestamps):
                detections.append(
                    BruteForceDetection(
                        detection_type=DetectionType.BRUTE_FORCE,
                        username=username,
                        failed_attempts=attempt_count,
                        risk_score=self.RISK_SCORE,
                        first_attempt_timestamp=first_ts,
                        last_attempt_timestamp=last_ts,
                    )
                )

        logger.info(f"Brute force detection run found {len(detections)} detection(s)")
        return detections

    def _find_bursts(self, timestamps: list[datetime]) -> list[tuple[datetime, datetime, int]]:
        """
        Scans sorted timestamps for one username and returns each
        non-overlapping burst that meets the threshold within the
        rolling window, as (first_timestamp, last_timestamp, count).
        """
        window = timedelta(minutes=self.WINDOW_MINUTES)
        bursts: list[tuple[datetime, datetime, int]] = []

        left = 0
        n = len(timestamps)
        for right in range(n):
            # Shrink the window from the left until it fits within the time limit
            while timestamps[right] - timestamps[left] > window:
                left += 1

            attempt_count = right - left + 1
            if attempt_count >= self.FAILED_ATTEMPTS_THRESHOLD:
                bursts.append((timestamps[left], timestamps[right], attempt_count))
                # Start the next window after this burst so a continuous
                # stream of failures isn't reported as many overlapping detections
                left = right + 1

        return bursts
