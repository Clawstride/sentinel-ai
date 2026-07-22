"""
New Device + Success Detection service.

Rule:
  - A user successfully authenticates using a device not previously
    observed for that username
  AND at least one additional suspicious signal:
    - a new IP address for that username, OR
    - an off-hours authentication time

MVP notes:
  - "Not previously observed" is judged against this username's own
    login history seen so far, scanned in chronological order. A
    user's very first-ever successful login is never flagged as a
    "new device" (there is no prior baseline yet to compare it to).
  - Off-hours uses the simple fixed UTC hour range from
    app/services/detection/common.py, not a statistical per-user
    baseline.
  - Fixed MVP risk score: 60 (Medium). Documented here because there's
    no natural formula for it yet — a new device plus one more signal
    is treated as moderately suspicious, less severe than a confirmed
    brute-force burst or a privileged-account event.
"""

import logging
from collections import defaultdict

from app.repositories.log_event_repository import LogEventRepository
from app.schemas.detection import DetectionType, NewDeviceDetection
from app.services.detection.common import is_off_hours

logger = logging.getLogger(__name__)


class NewDeviceDetectionService:
    """Detects new-device-plus-signal login patterns from stored authentication logs."""

    RISK_SCORE = 60

    def __init__(self, repository: LogEventRepository):
        self.repository = repository

    def detect(self) -> list[NewDeviceDetection]:
        """Runs new-device detection across all stored successful logins."""
        events = self.repository.get_successful_login_events()

        events_by_user: dict[str, list] = defaultdict(list)
        for event in events:
            events_by_user[event.username].append(event)

        detections: list[NewDeviceDetection] = []
        for username, user_events in events_by_user.items():
            user_events.sort(key=lambda e: e.timestamp)

            seen_devices: set[str] = set()
            seen_ips: set[str] = set()

            for event in user_events:
                # bool(seen_devices) guards the user's first-ever login:
                # there's no baseline yet, so it can never be "new".
                is_new_device = bool(seen_devices) and event.device not in seen_devices
                is_new_ip = bool(seen_ips) and event.ip_address not in seen_ips
                off_hours = is_off_hours(event.timestamp)

                if is_new_device and (is_new_ip or off_hours):
                    triggered_signals = ["new_device"]
                    if is_new_ip:
                        triggered_signals.append("new_ip")
                    if off_hours:
                        triggered_signals.append("off_hours")

                    detections.append(
                        NewDeviceDetection(
                            detection_type=DetectionType.NEW_DEVICE,
                            username=username,
                            device=event.device,
                            ip_address=event.ip_address,
                            timestamp=event.timestamp,
                            triggered_signals=triggered_signals,
                            risk_score=self.RISK_SCORE,
                        )
                    )

                seen_devices.add(event.device)
                seen_ips.add(event.ip_address)

        logger.info(f"New device detection run found {len(detections)} detection(s)")
        return detections
