"""
Repository layer for LogEvent.

The repository's only job is talking to the database. It knows
nothing about CSV files, HTTP, or validation — that logic lives in
the service layer (app/services/log_event_service.py). This
separation keeps persistence concerns isolated and easy to swap or
test independently.
"""

import logging

from sqlalchemy.orm import Session

from app.models.log_event import LogEvent

logger = logging.getLogger(__name__)


class LogEventRepository:
    """Handles all direct database operations for LogEvent rows."""

    def __init__(self, db: Session):
        self.db = db

    def bulk_insert(self, log_events: list[LogEvent]) -> int:
        """
        Inserts multiple LogEvent rows in a single transaction.

        Returns the number of rows inserted. Rolls back the whole
        batch if any row fails, so we never end up with a partially
        imported file.
        """
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
