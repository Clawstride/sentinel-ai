"""
Shared helpers used by multiple detection rules.

Kept separate from any single detection service so the fixed MVP
off-hours window is defined and documented in exactly one place.
"""

from datetime import datetime

# MVP off-hours window: a simple fixed UTC hour range rather than a
# statistical per-user baseline. Any authentication timestamp whose
# hour falls in [OFF_HOURS_START_HOUR, OFF_HOURS_END_HOUR) is treated
# as off-hours. Adjust these two constants to retune the window.
OFF_HOURS_START_HOUR = 0   # 12:00 AM UTC
OFF_HOURS_END_HOUR = 5     # 5:00 AM UTC (exclusive)


def is_off_hours(timestamp: datetime) -> bool:
    """Returns True if the given timestamp's hour falls within the off-hours window."""
    return OFF_HOURS_START_HOUR <= timestamp.hour < OFF_HOURS_END_HOUR
