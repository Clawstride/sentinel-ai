"""
Models package.

Importing every model here ensures they are registered on
Base.metadata as soon as app.models is imported anywhere
(including Alembic's env.py).
"""

from app.models.incident import Incident
from app.models.log_event import LogEvent

__all__ = ["LogEvent", "Incident"]
