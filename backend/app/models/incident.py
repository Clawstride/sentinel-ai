"""
Incident ORM model.

Represents a confirmed security incident, created from a detection
result (e.g. a Brute Force Detection). This is intentionally a plain
storage model — no detection logic or AI summarization belongs here.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
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

    # The evidence window this incident was built from: the span of
    # LogEvent timestamps that back it up. For range-based detections
    # (Brute Force, Impossible Travel) this is the first/last event of
    # the burst; for point detections (New Device, Privileged Login)
    # window_end is the triggering event and window_start is the prior
    # baseline event used for comparison (or the same timestamp if no
    # baseline exists). This is what the investigation endpoint uses to
    # reconstruct the timeline — see InvestigationService.
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Free-text analyst notes (Investigation Workspace, Feature 6).
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Incident incident_id={self.incident_id!r} username={self.username!r} status={self.status!r}>"
