"""
LogEvent ORM model.

Represents a single authentication log entry imported from a CSV
upload (Feature 1: Authentication Log Upload).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LogEvent(Base):
    """A single authentication log event imported from a CSV file."""

    __tablename__ = "log_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    device: Mapped[str] = mapped_column(String(255), nullable=False)
    login_status: Mapped[str] = mapped_column(String(50), nullable=False)
    is_privileged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<LogEvent id={self.id} username={self.username!r} "
            f"ip={self.ip_address!r} status={self.login_status!r}>"
        )
