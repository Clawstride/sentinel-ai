"""
Repository layer for LogEvent.

The repository's only job is talking to the database. It knows
nothing about CSV files, HTTP, or detection rules — that logic lives
in the service layer.
"""

import logging
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.log_event import LogEvent

logger = logging.getLogger(__name__)


class LogEventRepository:
    """Handles all direct database operations for LogEvent rows."""

    def __init__(self, db: Session):
        self.db = db

    def bulk_insert(self, log_events: list[LogEvent]) -> int:
        """Inserts multiple LogEvent rows in a single transaction."""
        if not log_events:
            return 0

        try:
            self.db.add_all(log_events)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("Database error while inserting log events")
            raise

        logger.info(f"Inserted {len(log_events)} log events into the database")
        return len(log_events)

    def get_failed_login_events(self) -> list[LogEvent]:
        """
        Returns all failed-login LogEvent rows, ordered by username then
        timestamp (ascending), ready for per-user chronological analysis.

        Matching on login_status is case-insensitive since the value comes
        from free-text CSV uploads (e.g. "FAILED", "Failed", "failed").
        """
        return (
            self.db.query(LogEvent)
            .filter(func.lower(LogEvent.login_status) == "failed")
            .order_by(LogEvent.username.asc(), LogEvent.timestamp.asc())
            .all()
        )

    def get_successful_login_events(self) -> list[LogEvent]:
        """
        Returns all successful-login LogEvent rows, ordered by username
        then timestamp (ascending). Used by Impossible Travel, New
        Device, and Suspicious Privileged Login detection, which all
        need each username's chronological successful-login history.

        Matching on login_status is case-insensitive since the value comes
        from free-text CSV uploads (e.g. "SUCCESS", "Success", "success").
        """
        return (
            self.db.query(LogEvent)
            .filter(func.lower(LogEvent.login_status) == "success")
            .order_by(LogEvent.username.asc(), LogEvent.timestamp.asc())
            .all()
        )

    def get_events_for_username_in_window(
        self, username: str, start: datetime, end: datetime
    ) -> list[LogEvent]:
        """
        Returns every LogEvent for one username with a timestamp between
        `start` and `end` (inclusive), ordered chronologically.

        Used by the Investigation Workspace to reconstruct the evidence
        timeline behind an incident, using the incident's stored
        window_start/window_end.
        """
        return (
            self.db.query(LogEvent)
            .filter(
                LogEvent.username == username,
                LogEvent.timestamp >= start,
                LogEvent.timestamp <= end,
            )
            .order_by(LogEvent.timestamp.asc())
            .all()
        )
