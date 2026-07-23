"""
Deterministic "why was this flagged" indicator generation.

CRITICAL: these indicators come ONLY from stored incident/log data —
no LLM is involved in deciding why something was detected. The AI
summary (app/services/investigation/ai_summary.py) receives these
indicators as already-determined facts; it never generates them.

Each detection type gets its own small builder function, dispatched by
incident_type. All context needed is either on the Incident row itself
(window_start/window_end, which detection created) or in the
reconstructed timeline (the LogEvent rows within that window).
"""

from app.models.incident import Incident
from app.models.log_event import LogEvent
from app.services.detection.common import is_off_hours

MINUTES_PER_SECOND_DIVISOR = 60


def build_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    """Dispatches to the right deterministic indicator builder for this incident's type."""
    builders = {
        "Brute Force": _brute_force_indicators,
        "Impossible Travel": _impossible_travel_indicators,
        "New Device Login": _new_device_indicators,
        "Suspicious Privileged Login": _privileged_login_indicators,
    }
    builder = builders.get(incident.incident_type, _generic_indicators)
    return builder(incident, timeline)


def _window_minutes(incident: Incident) -> int | None:
    if incident.window_start is None or incident.window_end is None:
        return None
    seconds = (incident.window_end - incident.window_start).total_seconds()
    return max(1, int(seconds // MINUTES_PER_SECOND_DIVISOR))


def _brute_force_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    indicators = []
    minutes = _window_minutes(incident)
    attempt_count = len(timeline)

    if attempt_count and minutes is not None:
        indicators.append(f"{attempt_count} failed login attempts detected within {minutes} minutes")
    elif minutes is not None:
        indicators.append(f"Failed login attempts detected within {minutes} minutes")

    indicators.append("Repeated authentication failures for the same account")
    return indicators


def _impossible_travel_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    indicators = []

    if len(timeline) >= 2:
        previous, current = timeline[0], timeline[-1]
        if previous.country != current.country:
            indicators.append(
                f"Successful authentication country changed from {previous.country} to {current.country}"
            )
        minutes = max(1, int((current.timestamp - previous.timestamp).total_seconds() // MINUTES_PER_SECOND_DIVISOR))
        indicators.append(f"Successful logins occurred {minutes} minutes apart")
        if previous.ip_address != current.ip_address:
            indicators.append("Source IP changed between logins")
    else:
        indicators.append("Successful authentication country changed within a short time window")

    return indicators


def _new_device_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    indicators = ["Successful authentication from a previously unseen device"]

    if len(timeline) >= 2:
        previous, current = timeline[0], timeline[-1]
        if previous.ip_address != current.ip_address:
            indicators.append("Source IP was not previously observed for this user")
        if is_off_hours(current.timestamp):
            indicators.append("Login occurred during an off-hours time window")
    elif timeline and is_off_hours(timeline[-1].timestamp):
        indicators.append("Login occurred during an off-hours time window")

    return indicators


def _privileged_login_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    indicators = ["Authentication involved a privileged account"]

    if timeline:
        current = timeline[-1]
        if len(timeline) >= 2:
            previous = timeline[0]
            if previous.ip_address != current.ip_address:
                indicators.append("Login occurred from a new IP address for this user")
            if previous.country != current.country:
                indicators.append("Login occurred from a new country for this user")
        if is_off_hours(current.timestamp):
            indicators.append("Login occurred during an off-hours time window")

    return indicators


def _generic_indicators(incident: Incident, timeline: list[LogEvent]) -> list[str]:
    """Fallback for any future detection type that hasn't added a specific builder yet."""
    return [f"Flagged by the '{incident.incident_type}' detection rule"]
