"""
Deterministic recommended investigation actions, one static list per
detection type. No AI involvement — these are fixed by the rule that
triggered the incident, and easy to extend by adding a new dict entry.
"""

RECOMMENDED_ACTIONS: dict[str, list[str]] = {
    "Brute Force": [
        "Review source IP activity",
        "Verify whether the account owner recognizes the attempts",
        "Consider temporary account protection or credential reset",
        "Review whether any successful login followed the failures",
    ],
    "Impossible Travel": [
        "Verify the activity with the affected user",
        "Check whether an approved VPN or proxy was used",
        "Review both authentication sessions",
        "Investigate credential compromise if activity is unauthorized",
    ],
    "New Device Login": [
        "Verify whether the user recognizes the device",
        "Review source IP and location",
        "Check recent authentication history",
    ],
    "Suspicious Privileged Login": [
        "Verify administrator activity",
        "Review privileged actions following authentication",
        "Check source IP/location",
        "Escalate if activity is unauthorized",
    ],
}

_DEFAULT_ACTIONS = ["Review the incident details and investigate further"]


def get_recommended_actions(incident_type: str) -> list[str]:
    """Returns the fixed recommended-action list for a detection type."""
    return RECOMMENDED_ACTIONS.get(incident_type, _DEFAULT_ACTIONS)
