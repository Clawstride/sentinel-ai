"""
Incident ORM model.

Represents a confirmed security incident, created from a detection
result (e.g. a Brute Force Detection). This is intentionally a plain
storage model — no detection logic or AI summarization belongs here.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Incident(Base):
    """A security incident generated from one or more detections."""

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Human-friendly identifier, e.g. "INC-000001". Generated from `id`
    # after insert (see IncidentRepository.create), so it's always
    # unique and sequential.
    incident_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open", server_default="Open")

    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Incident incident_id={self.incident_id!r} username={self.username!r} status={self.status!r}>"
