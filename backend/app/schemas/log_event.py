"""
Pydantic schemas for the Authentication Log Upload feature.

These define the request/response contracts for the API layer, kept
separate from the SQLAlchemy model (app/models/log_event.py) so that
API shape and DB schema can evolve independently.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# Columns that MUST be present in the uploaded CSV file.
REQUIRED_CSV_COLUMNS: list[str] = [
    "timestamp",
    "username",
    "ip_address",
    "country",
    "device",
    "login_status",
    "is_privileged",
]


class LogEventCreate(BaseModel):
    """Represents a single validated row, ready to be persisted."""

    timestamp: datetime
    username: str
    ip_address: str
    country: str
    device: str
    login_status: str
    is_privileged: bool


class LogEventRead(BaseModel):
    """Represents a LogEvent as returned by the API (not used by upload, kept for completeness)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    username: str
    ip_address: str
    country: str
    device: str
    login_status: str
    is_privileged: bool
    created_at: datetime


class LogUploadResponse(BaseModel):
    """Response returned after a successful CSV upload."""

    message: str = Field(..., examples=["Log file uploaded and processed successfully"])
    rows_imported: int = Field(..., examples=[128])
