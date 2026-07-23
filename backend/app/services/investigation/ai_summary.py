"""
AI-assisted incident summary — an explanation layer only.

Hard boundary (see module docstring for the whole feature, but worth
repeating right here): the LLM never detects anything, never assigns a
risk score or severity, and never invents evidence. It receives the
indicators, timeline, and metadata that the deterministic rule engine
already produced, and its only job is to phrase that into a short,
analyst-readable paragraph.

Works without any AI provider configured: if `settings.ANTHROPIC_API_KEY`
is unset, or the API call fails or times out for any reason, this
returns a deterministic, template-based summary instead. The
investigation endpoint never fails because of this module.

No new dependency is added for this — the request is a small, one-shot
JSON POST, so the standard library's urllib is enough and avoids
pulling in an HTTP client or the full Anthropic SDK for one call site.
"""

import json
import logging
import urllib.error
import urllib.request

from app.core.config import settings

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
REQUEST_TIMEOUT_SECONDS = 8
MAX_RESPONSE_TOKENS = 300

_SYSTEM_PROMPT = (
    "You are a security-analyst assistant inside SentinelAI. You will be given "
    "structured incident data that a deterministic rule-based detection engine has "
    "already produced (incident type, severity, risk score, indicators, timeline, "
    "recommended actions). Write a concise, factual, 2-4 sentence explanation of "
    "the incident for a human analyst.\n\n"
    "Strict rules you must follow:\n"
    "- Only use the facts given to you below. Do not invent events, IPs, countries, "
    "usernames, timestamps, or actions that are not present in the data.\n"
    "- Clearly explain why the deterministic system flagged this incident, using "
    "the given indicators.\n"
    "- Do not assign, change, or restate a different risk score, severity, or "
    "status than the ones given — those are already final.\n"
    "- Do not claim an attack is confirmed. Describe the activity as suspicious "
    "and requiring investigation.\n"
    "- Keep the response short and professional; no preamble, no bullet points."
)


def generate_ai_summary(context: dict) -> tuple[str, str]:
    """
    Returns (summary_text, generated_by), where generated_by is either
    "ai" or "fallback".
    """
    if not settings.ANTHROPIC_API_KEY:
        return _fallback_summary(context), "fallback"

    try:
        summary = _call_anthropic(context)
        return summary, "ai"
    except Exception:
        # Any failure (network, auth, timeout, malformed response) falls
        # back to the deterministic summary rather than breaking the
        # investigation endpoint.
        logger.exception("AI summary generation failed; using deterministic fallback")
        return _fallback_summary(context), "fallback"


def _call_anthropic(context: dict) -> str:
    user_message = f"Incident data (JSON):\n{json.dumps(context, default=str)}"

    request_body = json.dumps(
        {
            "model": settings.AI_SUMMARY_MODEL,
            "max_tokens": MAX_RESPONSE_TOKENS,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_message}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=request_body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": ANTHROPIC_API_VERSION,
        },
    )

    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))

    text_blocks = [block["text"] for block in payload.get("content", []) if block.get("type") == "text"]
    summary = " ".join(text_blocks).strip()

    if not summary:
        raise ValueError("Empty response from AI provider")

    return summary


def _fallback_summary(context: dict) -> str:
    """
    Deterministic, template-based summary. Used whenever no AI provider
    is configured, or the AI call fails for any reason — the
    investigation endpoint always returns a usable summary.
    """
    indicators = context.get("indicators") or []
    indicators_text = "; ".join(indicators) if indicators else "the configured detection rule"

    return (
        f"SentinelAI detected a '{context.get('incident_type')}' incident for user "
        f"'{context.get('username')}', producing a {context.get('severity')}-severity "
        f"incident with a risk score of {context.get('risk_score')}. "
        f"This was flagged because: {indicators_text}. "
        "This is suspicious activity that requires investigation; analysts should "
        "review the related authentication activity and confirm whether it was legitimate."
    )
